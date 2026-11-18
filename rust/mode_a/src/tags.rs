//! The class TAG a page string carries (`interactive/tags.py`, feature 134; ported by feature 449 T150, the engine port's step 2, the
//! Python deleted by its part B): the side-list value beside each drawn string. A key - the whole string is one class
//! (`"-"` is the not-highlighted ruling), a key marked as a feature's PLANTING (`Planted`, feature 153: the page's group opener adds a
//! token the stylesheet reaches, every other reader takes it as the key it is), a `Split` (one element whose fill is one class and whose
//! stroke another - a paddy and its bund), `Parts` (one string joined from pieces of several classes), or none (nobody ruled on it - what
//! the census reports).
//!
//! Research: plumbing - NONE

/// The not-highlighted ruling (`classes.NOT_HIGHLIGHTED`): ink the GM ruled out of the highlighting, counted under its own key.
pub const NOT_HIGHLIGHTED: &str = "-";

/// The title placard's reserved key (`classes.PLACE`): its modal is the place card, built per map.
pub const PLACE: &str = "place";

/// A class key, with whether it marks the planting on that feature (`tags.Planted`, a `str` subclass in the Python).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Key {
    pub name: String,
    pub planted: bool,
}

impl Key {
    /// A plain key.
    #[must_use]
    pub fn plain(name: &str) -> Self {
        Self {
            name: name.to_owned(),
            planted: false,
        }
    }
}

/// What one drawn string is tagged with (`tags.ClsTag`).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ClsTag {
    /// Nobody ruled on it (`None`).
    Unruled,
    /// One class for the whole string (`str`, or `Planted`).
    Key(Key),
    /// One element, its fill one class and its stroke another (`Split`).
    Split { fill: String, stroke: String },
    /// One string joined from pieces, each with its own class or none (`Parts`).
    Parts(Vec<(Option<Key>, String)>),
}

impl ClsTag {
    /// A plain key's tag.
    #[must_use]
    pub fn key(name: &str) -> Self {
        Self::Key(Key::plain(name))
    }

    /// The key, when the tag is one (a `str` to the Python's `isinstance`).
    #[must_use]
    pub fn as_key(&self) -> Option<&Key> {
        match self {
            Self::Key(k) => Some(k),
            _ => None,
        }
    }

    /// Whether the tag is the not-highlighted ruling (`tag == NOT_HIGHLIGHTED`: a `str` equal to `"-"`, planted or not).
    #[must_use]
    pub fn is_ruled_out(&self) -> bool {
        self.as_key().is_some_and(|k| k.name == NOT_HIGHLIGHTED)
    }

    /// Whether nobody ruled on it.
    #[must_use]
    pub fn is_unruled(&self) -> bool {
        matches!(self, Self::Unruled)
    }
}

#[cfg(test)]
mod tests {
    use super::{ClsTag, Key};

    #[test]
    fn a_tag_answers_what_it_is() {
        assert!(ClsTag::key("-").is_ruled_out());
        let planted = ClsTag::Key(Key {
            name: "-".into(),
            planted: true,
        });
        assert!(planted.is_ruled_out());
        assert!(!ClsTag::key("well").is_ruled_out());
        assert!(!ClsTag::Unruled.is_ruled_out());
        assert!(ClsTag::Unruled.is_unruled() && !ClsTag::key("a").is_unruled());
        let split = ClsTag::Split {
            fill: "a".into(),
            stroke: "b".into(),
        };
        assert_eq!(split.as_key(), None);
        assert_eq!(ClsTag::key("a").as_key(), Some(&Key::plain("a")));
    }
}
