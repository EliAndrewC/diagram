//! A conflicted `specs/*/plan.md` merged BY SECTION (feature 451 T300), from its three whole sides - the carried commit's parent
//! (the base), the clone's, the builder's - never from the conflict's hunks. A section is a `### T<n>` heading line with everything
//! down to the next such line, KEYED BY ITS WHOLE HEADING LINE (451 T419), which is unique where a task id is not: a task's
//! `### T<n>`, `### T<n> Approach`, checklist, `part 2` and `part B` headings are sections of their own. What stands before the
//! first is the opening.
//!
//! WHY: on 2026-11-26 most carries stopped on "a hunk both sides changed": a builder FILLS its task's stub and may REMOVE one (a
//! bundle's second section folded into the first), the clone meanwhile files other tasks' stubs or withdraws one, and the lines of
//! two stubs are near enough alike that the line merge sets one side's change against the other's addition (781644768b against
//! 1ceb830054's parent). The session resolved each by a script (`resolve3.py`, 2026-11-26), whose rule this is, its two silences
//! made stops. WHY BY HEADING (451 T419): keyed by task, a task whose sections stood in two places on any side stopped the carry,
//! and on 2026-11-27 two did - T355's on the clone's side and T308's on its commit's PARENT, which no later edit can fix - because
//! the session had appended three `part B` sections at the plan's end after a round arbiter's ruling. It resolved both by hand
//! (`resolve-heads.py`, kept at `/home/agent/.claude/jobs/c6fd72d1/tmp/`), whose rule this is.
//!
//! THE RULE, each section judged against the base with surrounding blank space ignored: the clone's order is kept; a section only
//! one side changed is that side's; one the builder removed is dropped and one the clone removed stays out, where the other side
//! left it alone; a section only the builder has is placed after the last section of its own task (at the end, for a task the
//! clone has none of). Then each task's sections are put together where its first stands, in their order: its heading, its
//! Approach, its performance checklist, then each `part <n>`'s the same way, then its `part B` ones - each kind in the order the
//! merge left it. It STOPS, saying which, where both sides changed one section differently, where each side added the same heading
//! differently, where both replaced one section with different headings (a stub filled on both sides), where one side removed a
//! section the other changed, where both changed the opening, or where a side holds one heading twice.

/// The digits of the task a plan heading `### T<n> ...` names: a bundle's first.
fn section_id(line: &str) -> Option<&str> {
    let rest = line.strip_prefix("### T")?;
    let digits = rest
        .find(|c: char| !c.is_ascii_digit())
        .unwrap_or(rest.len());
    (digits > 0).then(|| &rest[..digits])
}

/// A section: its heading line (the key, its line end aside) and its text.
type Section = (String, String);

/// A plan as its opening and its sections in order - or the heading it holds twice.
fn split(text: &str) -> Result<(String, Vec<Section>), String> {
    let mut opening = String::new();
    let mut sections: Vec<Section> = Vec::new();
    for line in text.split_inclusive('\n') {
        if section_id(line).is_some() {
            let head = line.trim_end().to_owned();
            if sections.iter().any(|s| s.0 == head) {
                return Err(head);
            }
            sections.push((head, line.to_owned()));
        } else if let Some(last) = sections.last_mut() {
            last.1.push_str(line);
        } else {
            opening.push_str(line);
        }
    }
    Ok((opening, sections))
}

/// A heading as a stop names it: its first 60 characters.
fn named(head: &str) -> String {
    let cut: String = head.chars().take(60).collect();
    if cut.len() < head.len() {
        format!("`{cut}...`")
    } else {
        format!("`{cut}`")
    }
}

/// Where a section stands among its task's: `part B` ones last, then by part (the first part 0), then heading, Approach,
/// performance checklist (the session's order, `resolve-heads.py`) - or none, for a heading of another kind (a `Decisions`, a
/// `notes`), which keeps its place after the section before it: older plans write those after their Approach, and a carry
/// reorders no tidy plan (measured 2026-11-27 over every `specs/*/plan.md`).
fn rank(head: &str) -> Option<(bool, u32, u8)> {
    // past the list of ids, `T1` or `T1, T2`
    let mut rest = head.trim_start_matches("### ");
    while let Some(after) = rest.strip_prefix('T') {
        let digits = after
            .find(|c: char| !c.is_ascii_digit())
            .unwrap_or(after.len());
        rest = after[digits..].trim_start_matches(',').trim_start();
    }
    if rest.starts_with("part B") {
        return Some((true, 0, 0));
    }
    let (part, rest) = rest
        .strip_prefix("part ")
        .and_then(|p| {
            let digits = p.find(|c: char| !c.is_ascii_digit()).unwrap_or(p.len());
            Some((p[..digits].parse().ok()?, p[digits..].trim_start()))
        })
        .unwrap_or((0, rest));
    let kind = if rest.is_empty() || rest.starts_with('(') {
        0
    } else if rest.starts_with("Approach") {
        1
    } else if rest.starts_with("Performance checklist") {
        2
    } else {
        return None;
    };
    Some((false, part, kind))
}

/// Do two texts say the same, the blank space around them aside?
fn same(a: &str, b: &str) -> bool {
    a.trim() == b.trim()
}

/// `text` appended to `out`, a blank line between them.
fn append(out: &mut String, text: &str) {
    if !out.is_empty() && !out.ends_with("\n\n") {
        out.push('\n');
    }
    out.push_str(text);
}

/// The sections of `merged` with each task's put together where its first stands, in [`rank`]'s order.
fn grouped(merged: Vec<Section>) -> Vec<Section> {
    let mut groups: Vec<(String, Vec<Section>)> = Vec::new();
    for section in merged {
        let id = section_id(&section.0).unwrap_or_default().to_owned();
        match groups.iter_mut().find(|g| g.0 == id) {
            Some(group) => group.1.push(section),
            None => groups.push((id, vec![section])),
        }
    }
    let mut out = Vec::new();
    for (_, group) in groups {
        let mut last = (false, 0, 0);
        let mut ranked: Vec<_> = group
            .into_iter()
            .map(|s| {
                last = rank(&s.0).unwrap_or(last);
                (last, s)
            })
            .collect();
        ranked.sort_by_key(|r| r.0);
        out.extend(ranked.into_iter().map(|r| r.1));
    }
    out
}

/// A section the base has that both sides removed, each adding a different heading of its task in its place (a stub both filled).
fn replaced_twice(base: &[Section], ours: &[Section], theirs: &[Section]) -> Option<String> {
    let has = |sections: &[Section], head: &str| sections.iter().any(|s| s.0 == head);
    // the headings of `id`'s task `side` added that the other side does not hold
    let added = |side: &[Section], other: &[Section], id: &str| {
        side.iter()
            .any(|s| section_id(&s.0) == Some(id) && !has(base, &s.0) && !has(other, &s.0))
    };
    base.iter()
        .filter(|(head, _)| !has(ours, head) && !has(theirs, head))
        .find(|(head, _)| {
            let id = section_id(head).unwrap_or_default();
            added(ours, theirs, id) && added(theirs, ours, id)
        })
        .map(|(head, _)| {
            format!(
                "both sides replaced the section {}, differently",
                named(head)
            )
        })
}

/// The plan of the three sides merged by section, or why it is left to a hand.
pub(super) fn merged(base: &str, ours: &str, theirs: &str) -> Result<String, String> {
    let side = |text: &str, whose: &str| {
        split(text).map_err(|head| format!("{whose} holds the heading {} twice", named(&head)))
    };
    let (base_opening, base) = side(base, "the carried commit's parent")?;
    let (our_opening, ours) = side(ours, "the clone's side")?;
    let (their_opening, theirs) = side(theirs, "the builder's side")?;
    let of = |sections: &[Section], head: &str| {
        sections.iter().find(|s| s.0 == head).map(|s| s.1.clone())
    };
    let opening = if same(&their_opening, &base_opening) || same(&their_opening, &our_opening) {
        our_opening
    } else if same(&our_opening, &base_opening) {
        their_opening
    } else {
        return Err("both sides changed the text before the first task's section".to_owned());
    };
    if let Some(why) = replaced_twice(&base, &ours, &theirs) {
        return Err(why);
    }
    let mut out: Vec<Section> = Vec::new();
    for (head, text) in &ours {
        let name = named(head);
        let kept = match (of(&base, head), of(&theirs, head)) {
            // only the clone has it, or the builder left it as it was
            (None, None) => Some(text.clone()),
            (Some(was), Some(their)) if same(&their, &was) => Some(text.clone()),
            // the builder removed it
            (Some(was), None) if same(text, &was) => None,
            (Some(_), None) => {
                return Err(format!(
                    "the builder removed the section {name}, which the clone changed"
                ))
            }
            // the builder changed it, or both sides wrote the same
            (Some(was), Some(their)) if same(text, &was) || same(text, &their) => Some(their),
            (None, Some(their)) if same(text, &their) => Some(text.clone()),
            (Some(_), Some(_)) => return Err(format!("both sides changed the section {name}")),
            (None, Some(_)) => {
                return Err(format!("both sides wrote the section {name}, differently"))
            }
        };
        out.extend(kept.map(|t| (head.clone(), t)));
    }
    for (head, text) in &theirs {
        if of(&ours, head).is_some() {
            continue;
        }
        match of(&base, head) {
            None => {
                // after the last section of its own task, else at the end
                let id = section_id(head);
                let at = out
                    .iter()
                    .rposition(|s| section_id(&s.0) == id)
                    .map_or(out.len(), |i| i + 1);
                out.insert(at, (head.clone(), text.clone()));
            }
            // the clone removed it and the builder left it alone
            Some(was) if same(text, &was) => {}
            Some(_) => {
                return Err(format!(
                    "the builder changed the section {}, which the clone removed",
                    named(head)
                ))
            }
        }
    }
    // a section after the one it followed on the clone's side is joined as it stood; one in a new place gets its blank line
    let mut merged = opening;
    let mut before: Option<String> = None;
    for (head, text) in grouped(out) {
        let after = |s: &Section| s.0 == head;
        let stood = match &before {
            None => ours.first().is_some_and(after),
            Some(b) => ours.windows(2).any(|w| w[0].0 == *b && after(&w[1])),
        };
        if stood {
            merged.push_str(&text);
        } else {
            append(&mut merged, &text);
        }
        before = Some(head);
    }
    Ok(merged)
}
