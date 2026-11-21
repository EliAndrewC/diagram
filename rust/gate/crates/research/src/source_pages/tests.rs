//! Saving pages for `source-reader` (feature 449 T145; the excerpt, the names and the numbers `source_pages.py`'s on the same input, 2026-11-16).

use std::os::unix::fs::PermissionsExt as _;
use std::path::Path;

use l7r_shared::tempdir::TempDir;

use super::*;
use crate::pages::{CachedPages, Inner};
use crate::verbatim::fetch::{Pages, Response, Transport};

const EXCERPT: &str = r"[EXCERPT of a 70,889-character page: its first 6,000 characters and 1,500 either side of the 3 of 5 quoted passage(s) found in it]
word0 word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12 word13 word14 word15 word16 word17 word18 word19 word20 word21 word22 word23 word24 word25 word26 word27 word28 word29 word30 word31 word32 word33 word34 word35 word36 word37 word38 word39 word40 word41 word42 word43 word44 word45 word46 word47 word48 word49 word50 word51 word52 word53 word54 word55 word56 word57 word58 word59 word60 word61 word62 word63 word64 word65 word66 word67 word68 word69 word70 word71 word72 word73 word74 word75 word76 word77 word78 word79 word80 word81 word82 word83 word84 word85 word86 word87 word88 word89 word90 word91 word92 word93 word94 word95 word96 word97 word98 word99 word100 word101 word102 word103 word104 word105 word106 word107 word108 word109 word110 word111 word112 word113 word114 word115 word116 word117 word118 word119 word120 word121 word122 word123 word124 word125 word126 word127 word128 word129 word130 word131 word132 word133 word134 word135 word136 word137 word138 word139 word140 word141 word142 word143 word144 word145 word146 word147 word148 word149 word150 word151 word152 word153 word154 word155 word156 word157 word158 word159 word160 word161 word162 word163 word164 word165 word166 word167 word168 word169 word170 word171 word172 word173 word174 word175 word176 word177 word178 word179 word180 word181 word182 word183 word184 word185 word186 word187 word188 word189 word190 word191 word192 word193 word194 word195 word196 word197 word198 word199 word200 word201 word202 word203 word204 word205 word206 word207 word208 word209 word210 word211 word212 word213 word214 word215 word216 word217 word218 word219 word220 word221 word222 word223 word224 word225 word226 word227 word228 word229 word230 word231 word232 word233 word234 word235 word236 word237 word238 word239 word240 word241 word242 word243 word244 word245 word246 word247 word248 word249 word250 word251 word252 word253 word254 word255 word256 word257 word258 word259 word260 word261 word262 word263 word264 word265 word266 word267 word268 word269 word270 word271 word272 word273 word274 word275 word276 word277 word278 word279 word280 word281 word282 word283 word284 word285 word286 word287 word288 word289 word290 word291 word292 word293 word294 word295 word296 word297 word298 word299 word300 word301 word302 word303 word304 word305 word306 word307 word308 word309 word310 word311 word312 word313 word314 word315 word316 word317 word318 word319 word320 word321 word322 word323 word324 word325 word326 word327 word328 word329 word330 word331 word332 word333 word334 word335 word336 word337 word338 word339 word340 word341 word342 word343 word344 word345 word346 word347 word348 word349 word350 word351 word352 word353 word354 word355 word356 word357 word358 word359 word360 word361 word362 word363 word364 word365 word366 word367 word368 word369 word370 word371 word372 word373 word374 word375 word376 word377 word378 word379 word380 word381 word382 word383 word384 word385 word386 word387 word388 word389 word390 word391 word392 word393 word394 word395 word396 word397 word398 word399 word400 word401 word402 word403 word404 word405 word406 word407 word408 word409 word410 word411 word412 word413 word414 word415 word416 word417 word418 word419 word420 word421 word422 word423 word424 word425 word426 word427 word428 word429 word430 word431 word432 word433 word434 word435 word436 word437 word438 word439 word440 word441 word442 word443 word444 word445 word446 word447 word448 word449 word450 word451 word452 word453 word454 word455 word456 word457 word458 word459 word460 word461 word462 word463 word464 word465 word466 word467 word468 word469 word470 word471 word472 word473 word474 word475 word476 word477 word478 word479 word480 word481 word482 word483 word484 word485 word486 word487 word488 word489 word490 word491 word492 word493 word494 word495 word496 word497 word498 word499 word500 word501 word502 word503 word504 word505 word506 word507 word508 word509 word510 word511 word512 word513 word514 word515 word516 word517 word518 word519 word520 word521 word522 word523 word524 word525 word526 word527 word528 word529 word530 word531 word532 word533 word534 word535 word536 word537 word538 word539 word540 word541 word542 word543 word544 word545 word546 word547 word548 word549 word550 word551 word552 word553 word554 word555 word556 word557 word558 word559 word560 word561 word562 word563 word564 word565 word566 word567 word568 word569 word570 word571 word572 word573 word574 word575 word576 word577 word578 word579 word580 word581 word582 word583 word584 word585 word586 word587 word588 word589 word590 word591 word592 word593 word594 word595 word596 word597 word598 word599 word600 word601 word602 word603 word604 word605 word606 word607 word608 word609 word610 word611 word612 word613 word614 word615 word616 word617 word618 word619 word620 word621 word622 word623 word624 word625 word626 word627 word628 word629 word630 word631 word632 word633 word634 word635 word636 word637 word638 word639 word640 word641 word642 word643 word644 word645 word646 word647 word648 word649 word650 word651 word652 word653 word654 word655 word656 word657 word658 word659 word660 word661 word662 word663 word664 word665 word666 word667 word668 word669 word670 word671 word672 word673 word674 word675 word676 word677 word678 word679 word680 word681 word682 word683 word684 word685 word686 word687 word688 word689 word690 word691 word692 word693 word694 word695 word696 word697 word698 word699 word700 word701 word702 word703 word704 word705 word706 word707 word708 word709 word710 word711 word712 word713 word714 word715 word716 word717 word718 word719 word720 word721 word722 word723 word724 word725 word726 word727 word728 word729 word730 word731 word732 word733 word734 word735 word736 word737 word738 word739 word740 word741 word742 word743 word744 word745 word746 word747 word748 word749 word750 word751 word752 word753 word754 word755 word756 word757 word758 word759 word760 word761 word762 word76

[... 18,390 characters not copied ...]
d2833 word2834 word2835 word2836 word2837 word2838 word2839 word2840 word2841 word2842 word2843 word2844 word2845 word2846 word2847 word2848 word2849 word2850 word2851 word2852 word2853 word2854 word2855 word2856 word2857 word2858 word2859 word2860 word2861 word2862 word2863 word2864 word2865 word2866 word2867 word2868 word2869 word2870 word2871 word2872 word2873 word2874 word2875 word2876 word2877 word2878 word2879 word2880 word2881 word2882 word2883 word2884 word2885 word2886 word2887 word2888 word2889 word2890 word2891 word2892 word2893 word2894 word2895 word2896 word2897 word2898 word2899 word2900 word2901 word2902 word2903 word2904 word2905 word2906 word2907 word2908 word2909 word2910 word2911 word2912 word2913 word2914 word2915 word2916 word2917 word2918 word2919 word2920 word2921 word2922 word2923 word2924 word2925 word2926 word2927 word2928 word2929 word2930 word2931 word2932 word2933 word2934 word2935 word2936 word2937 word2938 word2939 word2940 word2941 word2942 word2943 word2944 word2945 word2946 word2947 word2948 word2949 word2950 word2951 word2952 word2953 word2954 word2955 word2956 word2957 word2958 word2959 word2960 word2961 word2962 word2963 word2964 word2965 word2966 word2967 word2968 word2969 word2970 word2971 word2972 word2973 word2974 word2975 word2976 word2977 word2978 word2979 word2980 word2981 word2982 word2983 word2984 word2985 word2986 word2987 word2988 word2989 word2990 word2991 word2992 word2993 word2994 word2995 word2996 word2997 word2998 word2999 word3000 word3001 word3002 word3003 word3004 word3005 word3006 word3007 word3008 word3009 word3010 word3011 word3012 word3013 word3014 word3015 word3016 word3017 word3018 word3019 word3020 word3021 word3022 word3023 word3024 word3025 word3026 word3027 word3028 word3029 word3030 word3031 word3032 word3033 word3034 word3035 word3036 word3037 word3038 word3039 word3040 word3041 word3042 word3043 word3044 word3045 word3046 word3047 word3048 word3049 word3050 word3051 word3052 word3053 word3054 word3055 word3056 word3057 word3058 word3059 word3060 word3061 word3062 word3063 word3064 word3065 word3066 word3067 word3068 word3069 word3070 word3071 word3072 word3073 word3074 word3075 word3076 word3077 word3078 word3079 word3080 word3081 word3082 word3083 word3084 word3085 word3086 word3087 word3088 word3089 word3090 word3091 word3092 word3093 word3094 word3095 word3096 word3097 word3098 word3099 word3100 word3101 word3102 word3103 word3104 word3105 word3106 word3107 word3108 word3109 word3110 word3111 word3112 word3113 word3114 word3115 word3116 word3117 word3118 word3119 word3120 word3121 word3122 word3123 word3124 word3125 word3126 word3127 word3128 word3129 word3130 word3131 word3132 word3133 word3134 word3135 word3136 word3137 word3138 word3139 word3140 word3141 word3142 word3143 word3144 word3145 word3146 word3147 word3148 word3149 word3150 word3151 word3152 word3153 word3154 word3155 word3156 word3157 word3158 word3159 word3160 word3161 word3162 word3163 word3164 word3165 word3166 word3167 word3168 word3169 word3

[... 14,965 characters not copied ...]
d4833 word4834 word4835 word4836 word4837 word4838 word4839 word4840 word4841 word4842 word4843 word4844 word4845 word4846 word4847 word4848 word4849 word4850 word4851 word4852 word4853 word4854 word4855 word4856 word4857 word4858 word4859 word4860 word4861 word4862 word4863 word4864 word4865 word4866 word4867 word4868 word4869 word4870 word4871 word4872 word4873 word4874 word4875 word4876 word4877 word4878 word4879 word4880 word4881 word4882 word4883 word4884 word4885 word4886 word4887 word4888 word4889 word4890 word4891 word4892 word4893 word4894 word4895 word4896 word4897 word4898 word4899 word4900 word4901 word4902 word4903 word4904 word4905 word4906 word4907 word4908 word4909 word4910 word4911 word4912 word4913 word4914 word4915 word4916 word4917 word4918 word4919 word4920 word4921 word4922 word4923 word4924 word4925 word4926 word4927 word4928 word4929 word4930 word4931 word4932 word4933 word4934 word4935 word4936 word4937 word4938 word4939 word4940 word4941 word4942 word4943 word4944 word4945 word4946 word4947 word4948 word4949 word4950 word4951 word4952 word4953 word4954 word4955 word4956 word4957 word4958 word4959 word4960 word4961 word4962 word4963 word4964 word4965 word4966 word4967 word4968 word4969 word4970 word4971 word4972 word4973 word4974 word4975 word4976 word4977 word4978 word4979 word4980 word4981 word4982 word4983 word4984 word4985 word4986 word4987 word4988 word4989 word4990 word4991 word4992 word4993 word4994 word4995 word4996 word4997 word4998 word4999 word5000 word5001 word5002 word5003 word5004 word5005 word5006 word5007 word5008 word5009 word5010 word5011 word5012 word5013 word5014 word5015 word5016 word5017 word5018 word5019 word5020 word5021 word5022 word5023 word5024 word5025 word5026 word5027 word5028 word5029 word5030 word5031 word5032 word5033 word5034 word5035 word5036 word5037 word5038 word5039 word5040 word5041 word5042 word5043 word5044 word5045 word5046 word5047 word5048 word5049 word5050 word5051 word5052 word5053 word5054 word5055 word5056 word5057 word5058 word5059 word5060 word5061 word5062 word5063 word5064 word5065 word5066 word5067 word5068 word5069 word5070 word5071 word5072 word5073 word5074 word5075 word5076 word5077 word5078 word5079 word5080 word5081 word5082 word5083 word5084 word5085 word5086 word5087 word5088 word5089 word5090 word5091 word5092 word5093 word5094 word5095 word5096 word5097 word5098 word5099 word5100 word5101 word5102 word5103 word5104 word5105 word5106 word5107 word5108 word5109 word5110 word5111 word5112 word5113 word5114 word5115 word5116 word5117 word5118 word5119 word5120 word5121 word5122 word5123 word5124 word5125 word5126 word5127 word5128 word5129 word5130 word5131 word5132 word5133 word5134 word5135 word5136 word5137 word5138 word5139 word5140 word5141 word5142 word5143 word5144 word5145 word5146 word5147 word5148 word5149 word5150 word5151 word5152 word5153 word5154 word5155 word5156 word5157 word5158 word5159 word5160 word5161 word5162 word5163 word5164 word5165 word5166 word5167 word5168 word5169 word5170 word5171 word5172 word5173 word5174 word5175 word5

[... 23,893 characters not copied ...]
d7831 word7832 word7833 word7834 word7835 word7836 word7837 word7838 word7839 word7840 word7841 word7842 word7843 word7844 word7845 word7846 word7847 word7848 word7849 word7850 word7851 word7852 word7853 word7854 word7855 word7856 word7857 word7858 word7859 word7860 word7861 word7862 word7863 word7864 word7865 word7866 word7867 word7868 word7869 word7870 word7871 word7872 word7873 word7874 word7875 word7876 word7877 word7878 word7879 word7880 word7881 word7882 word7883 word7884 word7885 word7886 word7887 word7888 word7889 word7890 word7891 word7892 word7893 word7894 word7895 word7896 word7897 word7898 word7899 word7900 word7901 word7902 word7903 word7904 word7905 word7906 word7907 word7908 word7909 word7910 word7911 word7912 word7913 word7914 word7915 word7916 word7917 word7918 word7919 word7920 word7921 word7922 word7923 word7924 word7925 word7926 word7927 word7928 word7929 word7930 word7931 word7932 word7933 word7934 word7935 word7936 word7937 word7938 word7939 word7940 word7941 word7942 word7943 word7944 word7945 word7946 word7947 word7948 word7949 word7950 word7951 word7952 word7953 word7954 word7955 word7956 word7957 word7958 word7959 word7960 word7961 word7962 word7963 word7964 word7965 word7966 word7967 word7968 word7969 word7970 word7971 word7972 word7973 word7974 word7975 word7976 word7977 word7978 word7979 word7980 word7981 word7982 word7983 word7984 word7985 word7986 word7987 word7988 word7989 word7990 word7991 word7992 word7993 word7994 word7995 word7996 word7997 word7998 word7999
";

#[test]
fn a_long_page_is_cut_to_its_front_and_its_quotes() {
    let text = (0..8000)
        .map(|i| format!("word{i}"))
        .collect::<Vec<_>>()
        .join(" ");
    let quotes: Vec<String> = [
        "word3000 word3001 word3002 word3003".to_owned(),
        "word7998 word7999".to_owned(),
        "not on the page at all here".to_owned(),
        "x".to_owned(),
        (5000..5010)
            .map(|i| format!("word{i}"))
            .collect::<Vec<_>>()
            .join(" "),
    ]
    .into();
    assert_eq!(excerpt(&text, &quotes), EXCERPT);
    assert_eq!(excerpt("a b", &quotes), "a b");
    assert_eq!(
        file_for(3, "https://WWW.Ex_ample.org:8080/x"),
        "03-www.ex-ample.org-8080.txt"
    );
    assert_eq!(file_for(12, "relative"), "12-page.txt");
    assert_eq!(
        [0, 999, 1000, 1_234_567].map(thousands),
        ["0", "999", "1,000", "1,234,567"]
    );
    assert_eq!(
        fetch_url("https://github.com/a/b/blob/main/x/y.md"),
        "https://raw.githubusercontent.com/a/b/main/x/y.md"
    );
    assert_eq!(fetch_url("https://a.org"), "https://a.org");
    assert_eq!(
        [
            reason_ok("two words"),
            reason_ok("short x"),
            reason_ok("onlyoneword")
        ],
        [true, false, false]
    );
}

const LIST: &str = r#"{"domains": [{"domain": "bad.example", "reason": "machine text", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;

struct Net;

impl Transport for Net {
    fn open(&mut self, url: &str) -> std::result::Result<Response, String> {
        let body = match url {
            "http://a.org/p" => "<p>One. Two.</p>".to_owned(),
            "http://a.org/long" => format!("<p>{}</p>", "Line of text. ".repeat(3000)),
            _ => return Err("URLError: down".to_owned()),
        };
        Ok(Response {
            content_type: "text/html".into(),
            charset: String::new(),
            body: body.into_bytes(),
        })
    }
}

fn world(tag: &str) -> (TempDir, std::path::PathBuf) {
    let d = TempDir::new(tag);
    let root = d.join("c");
    std::fs::create_dir_all(root.join("research")).unwrap();
    std::fs::write(root.join("research/blocked-domains.json"), LIST).unwrap();
    (d, root)
}

fn cache(d: &Path, root: &Path) -> CachedPages {
    CachedPages::new(
        Inner::Pages(Pages::new(None, Box::new(Net))),
        &d.join("home"),
        false,
        false,
        root,
        &root.join("research"),
    )
}

#[test]
fn each_page_is_saved_and_listed_and_a_second_save_adds() {
    let (d, root) = world("research-source-pages");
    let out = d.join("out");
    let ledger = Ledger {
        home: d.join("home"),
        ctx: l7r_shared::consulted::context(&root).unwrap(),
        questions: vec!["0012".into()],
        root: root.clone(),
        sought: "the walls".into(),
    };
    let mut said = String::new();
    let urls: Vec<String> = [
        "http://a.org/p",
        "http://a.org/p",
        "http://a.org/long",
        "http://down.org/x",
        "https://bad.example/x",
    ]
    .map(str::to_owned)
    .into();
    let rows = save(
        &urls,
        &out,
        &mut cache(&d, &root),
        None,
        Some(&ledger),
        &mut said,
    )
    .unwrap();
    assert_eq!(rows.len(), 4);
    assert!(said.starts_with("sources-consulted: http://a.org/p - no earlier read on the ledger\nattempts: http://a.org/p - no earlier attempt\n"));
    let manifest = std::fs::read_to_string(out.join("MANIFEST.txt")).unwrap();
    assert!(manifest.starts_with("pointer | file | state\nhttp://a.org/p | 01-a.org.txt | FETCHED - 9 chars\nhttp://a.org/long | 02-a.org.p1.txt ... .p3.txt (3 parts - grep them all, read the part a hit is in) | FETCHED - "));
    assert!(manifest.contains("http://down.org/x | - | UNFETCHABLE - URLError: down\n"));
    assert!(manifest.contains("https://bad.example/x | - | UNFETCHABLE - a fetch refused"));
    assert_eq!(
        std::fs::read_to_string(out.join("01-a.org.txt")).unwrap(),
        "One.\nTwo.\n"
    );
    let logged = l7r_shared::attempts::read(&root, l7r_shared::attempts::LOG).unwrap();
    // an attempt for each pointer asked for, none for a blocked one
    assert_eq!(logged.len(), 3);
    assert_eq!(
        l7r_shared::consulted::read(&d.join("home")).unwrap().len(),
        2
    );
    // a second save keeps the fetched rows, retries the rest, and numbers past every file
    let mut again = String::new();
    let quotes = vec!["Line of text. Line".to_owned()];
    let urls2: Vec<String> = ["http://a.org/p", "http://down.org/x", "http://a.org/long"]
        .map(str::to_owned)
        .into();
    let rows = save(
        &urls2,
        &out,
        &mut cache(&d, &root),
        Some(&quotes),
        Some(&ledger),
        &mut again,
    )
    .unwrap();
    assert_eq!(rows.iter().filter(|r| r.state == "FETCHED").count(), 2);
    assert!(again.contains("sources-consulted: http://down.org/x - no earlier read on the ledger"));
    assert!(again.contains("read 1 time(s) before:") || !again.contains("http://a.org/p -"));
    assert_eq!(saved_rows(&out).unwrap().len(), 4);
    assert_eq!(next_number(&out).unwrap(), 3);
    let excerpted = save(
        &["http://a.org/new-long".to_owned()],
        &d.join("o2"),
        &mut cache(&d, &root),
        Some(&quotes),
        None,
        &mut String::new(),
    )
    .unwrap();
    assert_eq!(excerpted[0].state, "UNFETCHABLE");
    // a long page saved for named quotes is an excerpt; a page the cache holds says so; a ledger with nothing sought prints no attempts
    let quiet = Ledger {
        sought: String::new(),
        ..ledger
    };
    let mut said = String::new();
    let rows = save(
        &["http://a.org/long".to_owned()],
        &d.join("o3"),
        &mut cache(&d, &root),
        Some(&["Line of text. Line of".to_owned()]),
        Some(&quiet),
        &mut said,
    )
    .unwrap();
    assert!(
        rows[0].why.contains(", saved as an excerpt of ")
            && rows[0].why.contains(", from the page cache (fetched ")
    );
    assert!(!said.contains("attempts:"));
    let text = format!("{} tail", "word ".repeat(7000));
    assert!(excerpt(&text, &["word word word word".to_owned()])
        .ends_with("characters not copied ...]\n"));
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "every refusal of a save, one after another on one folder"
)]
fn what_save_refuses() {
    let (d, root) = world("research-source-pages-bad");
    let out = d.join("out");
    std::fs::create_dir_all(&out).unwrap();
    std::fs::write(out.join("MANIFEST.txt"), [0xff]).unwrap();
    assert!(saved_rows(&out).is_err());
    std::fs::set_permissions(
        out.join("MANIFEST.txt"),
        std::fs::Permissions::from_mode(0o000),
    )
    .unwrap();
    assert_eq!(saved_rows(&out).unwrap_err().kind, "OSError");
    std::fs::set_permissions(
        out.join("MANIFEST.txt"),
        std::fs::Permissions::from_mode(0o644),
    )
    .unwrap();
    std::fs::write(out.join("MANIFEST.txt"), [0xff]).unwrap();
    assert!(save(
        &[],
        &out,
        &mut cache(&d, &root),
        None,
        None,
        &mut String::new()
    )
    .is_err());
    std::fs::write(
        out.join("MANIFEST.txt"),
        "pointer | file | state\na | b\nc | d | FETCHED - why - more\n",
    )
    .unwrap();
    let rows = saved_rows(&out).unwrap();
    assert_eq!(
        (rows[0].state.as_str(), rows[1].why.as_str()),
        ("", "why - more")
    );
    save(
        &[],
        &out,
        &mut cache(&d, &root),
        None,
        None,
        &mut String::new(),
    )
    .unwrap();
    assert_eq!(
        std::fs::read_to_string(out.join("MANIFEST.txt")).unwrap(),
        "pointer | file | state\na | b | \nc | d | FETCHED - why - more\n"
    );
    assert!(next_number(&d.join("none")).is_err());
    std::fs::write(d.join("file"), "x").unwrap();
    assert!(save(
        &[],
        &d.join("file"),
        &mut cache(&d, &root),
        None,
        None,
        &mut String::new()
    )
    .is_err());
    std::fs::write(
        root.join("research/source-attempts.jsonl"),
        "{\"url\": \"a.org/p\", \"question\": \"0012\", \"outcome\": \"not-found\"}\n[1]\n",
    )
    .unwrap();
    assert!(judged_before(&root, "http://a.org/p", "0012").is_err());
    std::fs::write(
        root.join("research/source-attempts.jsonl"),
        "{\"url\": \"a.org/p\", \"question\": \"0012\", \"outcome\": \"not-found\"}\n",
    )
    .unwrap();
    assert_eq!(
        judged_before(&root, "http://a.org/p", "0012")
            .unwrap()
            .len(),
        1
    );
    assert!(judged_before(&root, "http://a.org/p", "0013")
        .unwrap()
        .is_empty());
    let ledger = Ledger {
        home: d.join("home"),
        ctx: serde_json::Map::new(),
        questions: Vec::new(),
        root: root.clone(),
        sought: "s".into(),
    };
    std::fs::create_dir_all(d.join("home")).unwrap();
    std::fs::write(d.join("home/sources-consulted.jsonl"), "[1]\n").unwrap();
    assert!(save(
        &["http://a.org/p".to_owned()],
        &d.join("o3"),
        &mut cache(&d, &root),
        None,
        Some(&ledger),
        &mut String::new()
    )
    .is_err());
    std::fs::write(
        d.join("home/sources-consulted.jsonl"),
        "{\"url\": \"a.org/p\", \"clone\": 5}\n",
    )
    .unwrap();
    assert!(save(
        &["http://a.org/p".to_owned()],
        &d.join("o4"),
        &mut cache(&d, &root),
        None,
        Some(&ledger),
        &mut String::new()
    )
    .is_err());
    std::fs::write(d.join("home/sources-consulted.jsonl"), "").unwrap();
    std::fs::write(root.join("research/source-attempts.jsonl"), "[1]\n").unwrap();
    assert!(save(
        &["http://a.org/p".to_owned()],
        &d.join("o5"),
        &mut cache(&d, &root),
        None,
        Some(&ledger),
        &mut String::new()
    )
    .is_err());
    std::fs::write(root.join("research/source-attempts.jsonl"), "").unwrap();
    std::fs::create_dir_all(d.join("o6/01-a.org.txt")).unwrap();
    assert!(save(
        &["http://a.org/p".to_owned()],
        &d.join("o6"),
        &mut cache(&d, &root),
        None,
        None,
        &mut String::new()
    )
    .is_ok());
    std::fs::create_dir_all(d.join("o7/MANIFEST.txt/x")).unwrap();
    assert!(save(
        &[],
        &d.join("o7"),
        &mut cache(&d, &root),
        None,
        None,
        &mut String::new()
    )
    .is_err());
    std::fs::write(root.join("research/blocked-domains.json"), "{").unwrap();
    assert!(save(
        &["http://a.org/q".to_owned()],
        &d.join("o8"),
        &mut cache(&d, &root),
        None,
        None,
        &mut String::new()
    )
    .is_err());
}
