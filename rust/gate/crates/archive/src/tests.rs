//! The crate's error (feature 449 T146).

use super::Error;

#[test]
fn an_error_reads_as_the_pythons_last_line() {
    let e = Error::new("Blocked", "refused");
    assert_eq!(e.to_string(), "Blocked: refused");
    let from: Error = l7r_gate_research::Error::new("RecordError", "bad").into();
    assert_eq!((from.kind, from.message.as_str()), ("RecordError", "bad"));
    let fault: Error = l7r_shared::blocked::Fault::new("BlockedListError", "x".to_owned()).into();
    assert_eq!(fault.kind, "BlockedListError");
}
