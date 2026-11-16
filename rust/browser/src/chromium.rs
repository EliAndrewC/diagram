//! Which Chromium, and how it is started (feature 449 T146). The binary is the one `scripts/container/chromium.pin` pins and
//! `scripts/container/install-chromium.sh` installs - Chrome for Testing's headless shell, byte for byte the build Playwright 1.62
//! launched - and it starts with Playwright's own switches, so a page renders, measures and crops as it did under Playwright.
//! `L7R_CHROMIUM` names another binary (the tests' stand-in); `L7R_CHROMIUM_HOME` moves the install, as it moves the script's.

use std::path::{Path, PathBuf};

use crate::cdp::Cdp;

/// The pin file, read at build time: one source for the script that installs Chromium, this crate and the gate's stamp.
pub const PIN: &str = include_str!("../../../scripts/container/chromium.pin");

/// A `NAME=value` line of the pin file.
#[must_use]
pub fn pinned(name: &str) -> String {
    PIN.lines()
        .find_map(|l| l.strip_prefix(name)?.strip_prefix('='))
        .unwrap_or_default()
        .to_owned()
}

/// The browser's executable: `L7R_CHROMIUM`, else the pinned version under `L7R_CHROMIUM_HOME` (default `~/.cache/l7r-chromium`).
#[must_use]
pub fn executable(var: &dyn Fn(&str) -> String) -> PathBuf {
    let named = var("L7R_CHROMIUM");
    if !named.is_empty() {
        return PathBuf::from(named);
    }
    let home = var("L7R_CHROMIUM_HOME");
    let base = if home.is_empty() {
        PathBuf::from(var("HOME")).join(".cache/l7r-chromium")
    } else {
        PathBuf::from(home)
    };
    base.join(pinned("CHROMIUM_VERSION"))
        .join("chrome-headless-shell-linux64/chrome-headless-shell")
}

/// The environment, as [`executable`] reads it.
#[must_use]
pub fn env_var(name: &str) -> String {
    std::env::var(name).unwrap_or_default()
}

/// Playwright 1.62's launch switches for headless Chromium, in its order (its `chromiumSwitches` and the headless additions, read off
/// its launch line, observed 2026-11-16 with `DEBUG=pw:browser`). Every one changes what a page does or draws in some case - the
/// color profile, the hover media, the features Playwright turns off - so they are kept whole.
const SWITCHES: &[&str] = &[
    "--disable-field-trial-config",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-back-forward-cache",
    "--disable-breakpad",
    "--disable-client-side-phishing-detection",
    "--disable-component-extensions-with-background-pages",
    "--disable-component-update",
    "--no-default-browser-check",
    "--disable-default-apps",
    "--disable-dev-shm-usage",
    "--disable-edgeupdater",
    "--disable-extensions",
    "--disable-features=AvoidUnnecessaryBeforeUnloadCheckSync,BoundaryEventDispatchTracksNodeRemoval,DestroyProfileOnBrowserClose,\
DialMediaRouteProvider,GlobalMediaControls,HttpsUpgrades,LensOverlay,MediaRouter,PaintHolding,ThirdPartyStoragePartitioning,\
BlockOriginHeaderModificationOnRedirect,Translate,AutoDeElevate,OptimizationHints,msForceBrowserSignIn,\
msEdgeUpdateLaunchServicesPreferredVersion",
    "--enable-features=CDPScreenshotNewSurface",
    "--allow-pre-commit-input",
    "--disable-hang-monitor",
    "--disable-ipc-flooding-protection",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-renderer-backgrounding",
    "--disable-updater-scheduler",
    "--force-color-profile=srgb",
    "--metrics-recording-only",
    "--no-first-run",
    "--password-store=basic",
    "--use-mock-keychain",
    "--no-service-autorun",
    "--export-tagged-pdf",
    "--disable-search-engine-choice-screen",
    "--unsafely-disable-devtools-self-xss-warnings",
    "--edge-skip-compat-layer-relaunch",
    "--disable-infobars",
    "--disable-search-engine-choice-screen",
    "--disable-sync",
    "--enable-unsafe-swiftshader",
    "--headless",
    "--hide-scrollbars",
    "--mute-audio",
    "--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4",
    "--no-sandbox",
];

/// The whole argument list for a profile in `profile`.
#[must_use]
pub fn arguments(profile: &Path) -> Vec<String> {
    let mut out: Vec<String> = SWITCHES.iter().map(|s| (*s).to_owned()).collect();
    out.push(format!("--user-data-dir={}", profile.display()));
    out.push("--remote-debugging-pipe".to_owned());
    out.push("--no-startup-window".to_owned());
    out
}

/// A browser running on a profile and a temporary directory of its own, both removed when it closes.
pub struct Launched {
    pub cdp: Cdp,
    profile: PathBuf,
}

impl Launched {
    /// Starts the browser [`executable`] names, on a new profile directory (Chromium makes it) and a temporary directory, both in one
    /// scratch directory under the temporary directory.
    ///
    /// # Errors
    /// The browser is not installed, cannot start, or does not answer.
    pub fn start(var: &dyn Fn(&str) -> String) -> Result<Self, String> {
        let exe = executable(var);
        if !exe.is_file() {
            return Err(format!(
                "no Chromium at {} - run scripts/container/install-chromium.sh",
                exe.display()
            ));
        }
        let scratch = std::env::temp_dir().join(format!(
            "l7r-browser-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map_or(0, |d| d.as_nanos())
        ));
        // ITS OWN TEMPORARY DIRECTORY: with `--disable-dev-shm-usage` Chromium keeps its shared memory in `$TMPDIR`, and left a
        // `.org.chromium.Chromium.*` there after a clean close (observed 2026-11-16, `make rust-test`'s check of the tests' TMPDIR); under
        // the scratch directory it goes with the profile
        let tmp = scratch.join("tmp");
        let _ = std::fs::create_dir_all(&tmp);
        let cdp = Cdp::launch_with(
            Path::new("/bin/sh"),
            &exe,
            &arguments(&scratch.join("profile")),
            Some(&tmp),
        );
        let mut launched = Self {
            cdp: cdp?,
            profile: scratch,
        };
        launched
            .cdp
            .call("Browser.getVersion", serde_json::json!({}), None)?;
        Ok(launched)
    }
}

impl Drop for Launched {
    fn drop(&mut self) {
        self.cdp.close();
        let _ = std::fs::remove_dir_all(&self.profile);
    }
}

#[cfg(test)]
mod tests;
