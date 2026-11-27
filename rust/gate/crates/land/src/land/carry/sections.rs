//! A conflicted `specs/*/plan.md` merged BY SECTION (feature 451 T300), from its three whole sides - the carried commit's parent
//! (the base), the clone's, the builder's - never from the conflict's hunks. A section is a `### T<n>` heading with everything down
//! to the next task's (a task's `### T<n> Approach` and checklist headings are its own); what stands before the first is the
//! opening.
//!
//! WHY: on 2026-11-26 most carries stopped on "a hunk both sides changed": a builder FILLS its task's stub and may REMOVE one (a
//! bundle's second section folded into the first), the clone meanwhile files other tasks' stubs or withdraws one, and the lines of
//! two stubs are near enough alike that the line merge sets one side's change against the other's addition (781644768b against
//! 1ceb830054's parent: the clone withdrew the plan's last stub, the builder filed six after it). The session resolved each by a
//! script (`resolve3.py`, 2026-11-26), whose rule this is, its two silences made stops.
//!
//! THE RULE, each section judged against the base with surrounding blank space ignored: the clone's order is kept; a section only
//! one side changed is that side's; one the builder removed is dropped and one the clone removed stays out, where the other side
//! left it alone; the sections only the builder has are appended in its order. It STOPS, saying which, where both sides changed
//! one section differently, where each side added the same task's section differently, where one side removed a section the other
//! changed, where both changed the opening, or where a side holds one task's sections in two places.

/// The digits of the task a plan heading `### T<n> ...` names.
fn section_id(line: &str) -> Option<&str> {
    let rest = line.strip_prefix("### T")?;
    let digits = rest
        .find(|c: char| !c.is_ascii_digit())
        .unwrap_or(rest.len());
    (digits > 0).then(|| &rest[..digits])
}

/// A plan as its opening and its tasks' sections in order, `(id, text)` - or the task whose sections stand in two places.
fn split(text: &str) -> Result<(String, Vec<(String, String)>), String> {
    let mut opening = String::new();
    let mut sections: Vec<(String, String)> = Vec::new();
    for line in text.split_inclusive('\n') {
        let id = section_id(line);
        // a heading of the section in hand, or of a task met before
        let on = id.is_some() && sections.last().map(|s| s.0.as_str()) == id;
        if let Some(id) = id.filter(|id| !on && sections.iter().any(|s| s.0 == *id)) {
            return Err(id.to_owned());
        }
        match (id, sections.last_mut()) {
            (Some(id), _) if !on => sections.push((id.to_owned(), line.to_owned())),
            (_, Some(last)) => last.1.push_str(line),
            (_, None) => opening.push_str(line),
        }
    }
    Ok((opening, sections))
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

/// The plan of the three sides merged by section, or why it is left to a hand.
pub(super) fn merged(base: &str, ours: &str, theirs: &str) -> Result<String, String> {
    let side = |text: &str, whose: &str| {
        split(text).map_err(|id| format!("{whose} holds T{id}'s sections in two places"))
    };
    let (base_opening, base) = side(base, "the carried commit's parent")?;
    let (our_opening, ours) = side(ours, "the clone's side")?;
    let (their_opening, theirs) = side(theirs, "the builder's side")?;
    let of = |sections: &[(String, String)], id: &str| {
        sections.iter().find(|s| s.0 == id).map(|s| s.1.clone())
    };
    let mut out = if same(&their_opening, &base_opening) || same(&their_opening, &our_opening) {
        our_opening
    } else if same(&our_opening, &base_opening) {
        their_opening
    } else {
        return Err("both sides changed the text before the first task's section".to_owned());
    };
    for (id, text) in &ours {
        match (of(&base, id), of(&theirs, id)) {
            // only the clone has it, or the builder left it as it was
            (None, None) => out.push_str(text),
            (Some(was), Some(their)) if same(&their, &was) => out.push_str(text),
            // the builder removed it
            (Some(was), None) if same(text, &was) => {}
            (Some(_), None) => {
                return Err(format!(
                    "the builder removed T{id}'s section, which the clone changed"
                ))
            }
            // the builder changed it, or both sides wrote the same
            (Some(was), Some(their)) if same(text, &was) || same(text, &their) => {
                out.push_str(&their);
            }
            (None, Some(their)) if same(text, &their) => out.push_str(text),
            (Some(_), Some(_)) => return Err(format!("both sides changed T{id}'s section")),
            (None, Some(_)) => {
                return Err(format!("both sides wrote T{id}'s section, differently"))
            }
        }
    }
    for (id, text) in &theirs {
        if of(&ours, id).is_some() {
            continue;
        }
        match of(&base, id) {
            None => append(&mut out, text),
            // the clone removed it and the builder left it alone
            Some(was) if same(text, &was) => {}
            Some(_) => {
                return Err(format!(
                    "the builder changed T{id}'s section, which the clone removed"
                ))
            }
        }
    }
    Ok(out)
}
