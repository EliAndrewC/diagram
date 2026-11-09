//! The CI bucket's whole lifecycle document (feature 177 FR-013, from `ci/cachepolicy.py`, whose git history holds the reasoning for each horizon). The API overwrites, so this owns the whole document; `cache_location`'s key
//! bounds the count of objects, and these rules bound their age. S3 applies the shortest expiration among overlapping rules, so `cache/` (over 1 MiB, and so under the size rule too) keeps 30 days in both. `expire-ci-junk`, the 14-day
//! catch-all that also expired `verified/`, is retired: lifecycle rules have no negative filter, so the net is a size, and a 200-byte verified record, kept 365 days as evidence, is out of its reach. Rule 4 is separate because S3 refuses a multipart abort beside an object-size filter (measured on the live bucket 2026-09-03), and carrying no expiration it
//! cannot delete an object.

use serde_json::{json, Value};

pub(crate) const VERIFIED_RULE_ID: &str = "expire-verified-records";

/// The `put_bucket_lifecycle_configuration` document, returned rather than applied so that it can be read in a diff.
pub(crate) fn lifecycle_configuration() -> Value {
    json!({"Rules": [
        {"ID": "expire-generation-cache", "Status": "Enabled", "Filter": {"Prefix": "cache/"}, "Expiration": {"Days": 30}},
        {"ID": VERIFIED_RULE_ID, "Status": "Enabled", "Filter": {"Prefix": "verified/"}, "Expiration": {"Days": 365}},
        {"ID": "expire-large-objects", "Status": "Enabled", "Filter": {"ObjectSizeGreaterThan": 1_048_576}, "Expiration": {"Days": 30}},
        {"ID": "abort-dead-multipart-uploads", "Status": "Enabled", "Filter": {"Prefix": ""}, "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}},
    ]})
}

/// One rule of the document, by id: an index is a claim about order that nothing in the document guarantees.
pub(crate) fn rule(document: &Value, id: &str) -> Result<Value, String> {
    let rules = document["Rules"].as_array().map_or(&[][..], Vec::as_slice);
    rules
        .iter()
        .find(|r| r["ID"] == id)
        .cloned()
        .ok_or(format!("no lifecycle rule {id}"))
}

/// `l7r-gate lifecycle [rule id]`.
pub(crate) fn cli(args: &[String]) -> crate::Reply {
    let document = lifecycle_configuration();
    let answer = args
        .first()
        .map_or(Ok(document.clone()), |id| rule(&document, id));
    match answer {
        Ok(value) => crate::Reply {
            stdout: format!("{value}\n"),
            stderr: String::new(),
            code: 0,
        },
        Err(why) => crate::Reply {
            stdout: String::new(),
            stderr: format!("{why}\n"),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests {
    use super::{cli, lifecycle_configuration, rule, VERIFIED_RULE_ID};
    use serde_json::Value;

    fn rules() -> Vec<Value> {
        lifecycle_configuration()["Rules"]
            .as_array()
            .unwrap()
            .clone()
    }

    #[test]
    fn verified_records_are_out_of_the_junk_horizon_and_nothing_is_immortal() {
        let verified = rules()
            .into_iter()
            .find(|r| r["ID"] == VERIFIED_RULE_ID)
            .unwrap();
        assert_eq!(verified["Expiration"]["Days"], 365);
        assert!(rules()
            .iter()
            .all(|r| r["Status"] == "Enabled" && r["ID"] != "expire-ci-junk"));
    }

    #[test]
    fn the_one_bare_prefix_carries_no_expiration_and_the_net_is_by_size() {
        let bare: Vec<Value> = rules()
            .into_iter()
            .filter(|r| r["Filter"]["Prefix"] == "")
            .collect();
        assert_eq!(bare.len(), 1);
        assert!(
            bare[0].get("Expiration").is_none()
                && bare[0]["AbortIncompleteMultipartUpload"]["DaysAfterInitiation"] == 7
        );
        assert!(rules()
            .iter()
            .any(|r| r["Filter"]["ObjectSizeGreaterThan"] == 1_048_576
                && r["Expiration"]["Days"] == 30));
    }

    #[test]
    fn a_rule_is_addressed_by_id_and_a_missing_one_is_loud() {
        let doc = lifecycle_configuration();
        assert_eq!(
            rule(&doc, VERIFIED_RULE_ID).unwrap()["Expiration"]["Days"],
            365
        );
        assert_eq!(
            rule(&doc, "nonsense").unwrap_err(),
            "no lifecycle rule nonsense"
        );
        assert!(cli(&[]).stdout.contains("expire-large-objects"));
        assert!(cli(&[VERIFIED_RULE_ID.to_owned()]).stdout.contains("365"));
        assert_eq!(cli(&["nonsense".to_owned()]).code, 1);
    }
}
