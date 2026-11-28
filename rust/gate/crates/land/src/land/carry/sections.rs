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
//!
//! ARCHIVE MARKERS ARE THE CLONE'S (461 T74): a landing's archive step moves finished sections to plan-done.md and writes a
//! `<!-- plan-archive: ... -->` line where they stood, on the TAIL of the section before them - often a hand-in's stub. Each
//! text is judged by its words, its markers aside; a section whose words only the builder changed takes the builder's words
//! and the clone's tail (its blank lines and markers); a section the builder removed hands the clone's markers in it to the
//! text before it. A section the clone archived and the builder left alone is dropped by the rule above, and one the builder
//! changed still stops. It stops where the clone's markers stand among a section's words, where the builder's are taken.
//! WHY: on 2026-11-28 the carry stopped five times on "both sides changed" a stub the builder filled and a landing had put a
//! marker on (461 T69, T22, T56/T64, T71), and stopped the lane's batch 461-1 at T71 (e26824a7a8); the session resolved each by
//! hand, keeping the clone's markers and the builder's filled stub. Merged by this rule, that case differs from the session's
//! hand resolution (d28a49d733) by two blank lines.

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

/// A landing's archive marker, `<!-- plan-archive: T<a> to T<b> moved to plan-done.md ... -->` (feature 375 FR-044): the line it
/// writes where it moved finished sections out, which stands on the tail of the section before them.
fn marker(line: &str) -> bool {
    line.trim_start().starts_with("<!-- plan-archive:")
}

/// A text's lines but its archive markers.
fn unmarked(text: &str) -> String {
    text.split_inclusive('\n').filter(|l| !marker(l)).collect()
}

/// Do two texts say the same, their archive markers and the blank space around them aside?
fn same_words(a: &str, b: &str) -> bool {
    same(&unmarked(a), &unmarked(b))
}

/// The clone's TAIL of a section: its blank lines and archive markers after its last line of words - or the heading of a
/// section whose markers stand among its words, which no rule places in another side's text.
fn tail<'a>(text: &'a str, head: &str) -> Result<&'a str, String> {
    let mut end = 0;
    let mut amid = false;
    let mut at = 0;
    for line in text.split_inclusive('\n') {
        at += line.len();
        if marker(line) {
            amid = true;
        } else if !line.trim().is_empty() {
            if amid {
                return Err(format!(
                    "the clone's archive markers stand among the words of the section {}",
                    named(head)
                ));
            }
            amid = false;
            end = at;
        }
    }
    Ok(&text[end..])
}

/// The builder's words of a section the clone changed only by its archive markers: the builder's text, its own markers out,
/// then the clone's tail - or the builder's text as it is where neither side holds a marker.
fn joined(theirs: &str, ours: &str, head: &str) -> Result<String, String> {
    let kept = tail(ours, head)?;
    if !theirs
        .split_inclusive('\n')
        .chain(kept.split_inclusive('\n'))
        .any(marker)
    {
        return Ok(theirs.to_owned());
    }
    let words = unmarked(theirs);
    Ok(format!("{}\n{kept}", words.trim_end()))
}

/// Of a text both sides hold, beside the base's: the clone's, the builder's, or the builder's words with the clone's markers
/// ([`joined`]) - or none, where both changed its words.
fn chosen(was: &str, ours: &str, theirs: &str, head: &str) -> Result<Option<String>, String> {
    Ok(Some(if same(theirs, was) || same_words(theirs, ours) {
        ours.to_owned()
    } else if same(ours, was) {
        theirs.to_owned()
    } else if same_words(theirs, was) {
        // the builder changed its markers alone: the clone's are the landing's
        ours.to_owned()
    } else if same_words(ours, was) {
        joined(theirs, ours, head)?
    } else {
        return Ok(None);
    }))
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
    let Some(mut opening) = chosen(&base_opening, &our_opening, &their_opening, "the opening")?
    else {
        return Err("both sides changed the text before the first task's section".to_owned());
    };
    if let Some(why) = replaced_twice(&base, &ours, &theirs) {
        return Err(why);
    }
    let mut out: Vec<Section> = Vec::new();
    for (head, text) in &ours {
        let name = named(head);
        let kept = match (of(&base, head), of(&theirs, head)) {
            // only the clone has it
            (None, None) => Some(text.clone()),
            // the builder removed it, where the clone changed no more than its markers: those go to the text before it
            (Some(was), None) if same_words(text, &was) => {
                let markers: String = text.split_inclusive('\n').filter(|l| marker(l)).collect();
                if !markers.is_empty() {
                    // a text before a section ends at its line end
                    out.last_mut()
                        .map_or(&mut opening, |s| &mut s.1)
                        .push_str(&markers);
                }
                None
            }
            (Some(_), None) => {
                return Err(format!(
                    "the builder removed the section {name}, which the clone changed"
                ))
            }
            // the builder left it, changed it, or both sides wrote the same (the clone's archive markers kept)
            (Some(was), Some(their)) => match chosen(&was, text, &their, head)? {
                Some(t) => Some(t),
                None => return Err(format!("both sides changed the section {name}")),
            },
            (None, Some(their)) if same_words(text, &their) => Some(text.clone()),
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
            // the clone removed it (archived it, as a landing does) and the builder left its words alone
            Some(was) if same_words(text, &was) => {}
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

#[cfg(test)]
mod tests;
