# Release Notes

## March 2026

### Features

- [`58c4d6cc`](https://github.com/stitch-05/paraguay-tax-automation/commit/58c4d6cc80031426467b019736da6d0a81ae0302): Add pip fallback support and improve dependency management in installation and update scripts.
- [`832ce48d`](https://github.com/stitch-05/paraguay-tax-automation/commit/832ce48db070be0b753196c63773621065aad572): Add development-mode install/update support and improve setup documentation.
- [`51b8f424`](https://github.com/stitch-05/paraguay-tax-automation/commit/51b8f424b2b2d22242776bb855cab9675bc9197f): Add update script to automate pulling latest changes and updating dependencies.
- [`b3309701`](https://github.com/stitch-05/paraguay-tax-automation/commit/b33097017b5f69f4d79dca0e2c1365599a7d5df8): Add comprehensive test suite for form handlers and improve notification handling.
- [`d334b3c9`](https://github.com/stitch-05/paraguay-tax-automation/commit/d334b3c9423cbf9d3c30536afb2336981f2814a6): Add mockup mode support for testing and development without server access.
- [`bce5b792`](https://github.com/stitch-05/paraguay-tax-automation/commit/bce5b792d9658e1b8a0a3009fdf744410492bd8d): Enhance AnimatedWaitContext with failure handling for robust operation tracking.
- [`aefb3bfc`](https://github.com/stitch-05/paraguay-tax-automation/commit/aefb3bfcc203077b7c5a1506a36ed3c6a88b7a18): Add debug option to AnimatedWaitContext for improved logging during operations.

### Bug Fixes

- [`4431861f`](https://github.com/stitch-05/paraguay-tax-automation/commit/4431861ff3b39f5ee5111ad7de84bc13c7a3ed58): Remove unnecessary Poetry lock command from the update script to prevent update flow issues.
- [`42932d3d`](https://github.com/stitch-05/paraguay-tax-automation/commit/42932d3de61cb1bbbc4ccf525a6d143382edad5a): Fix import statements for Cryptodome and update requirements for compatibility.
- [`d351207e`](https://github.com/stitch-05/paraguay-tax-automation/commit/d351207e4e68e6a431b1e169c2619992825ea793): Change HTTP method from POST to GET for submitting receipt form in Form955Handler.
- [`e7e9500a`](https://github.com/stitch-05/paraguay-tax-automation/commit/e7e9500ac6d8a6c40c4805414200bf2c332a5dc7): Improve completion message handling in mockup mode for clearer output.
- [`ae10a948`](https://github.com/stitch-05/paraguay-tax-automation/commit/ae10a948b714f9e351c9d017b638cd282fe03e30): Conditionally use animated wait context for notification sending to reduce overhead.
- [`6909b4b4`](https://github.com/stitch-05/paraguay-tax-automation/commit/6909b4b40307f2161b038da93417d9b875f99a36): Add detailed error logging for JSON decode failures in form handlers.

### Documentation

- [`8cfd645d`](https://github.com/stitch-05/paraguay-tax-automation/commit/8cfd645d4444d4920eddb30e9ddcbc89fe51a5e0): Update documentation for handler patterns and AI-assisted development guidelines.
- [`428573f8`](https://github.com/stitch-05/paraguay-tax-automation/commit/428573f8ff8902055c60eef83726ae5102e36e6a): Update documentation structure and content in copilot instructions for better guidance.

---

## February 2026

### Features

- [`c8376725`](https://github.com/stitch-05/paraguay-tax-automation/commit/c8376725fd8a3ab8a6381b78b07275c873d72cb1): Allow mockup mode to bypass tax-period validation in the main workflow.
- [`c2938185`](https://github.com/stitch-05/paraguay-tax-automation/commit/c293818574f9a4f612ac6eee112403311c530464): Refactor process method parameters for consistency across form handlers.
- [`ecb91975`](https://github.com/stitch-05/paraguay-tax-automation/commit/ecb9197513d13702b05bbfb5c3b0120fbd29b91b): Add animated console outputs for improved user experience during automation.
- [`2d2075ff`](https://github.com/stitch-05/paraguay-tax-automation/commit/2d2075fffecec06e8fb941e11cac350b98754459): Switch to NopeCHA free tier for captcha solving with better cost efficiency.
- [`89a0a9c5`](https://github.com/stitch-05/paraguay-tax-automation/commit/89a0a9c5b451105c231292e8a364c10550701819): Add notification message printing for better visibility of sent notifications.
- [`82ca6b24`](https://github.com/stitch-05/paraguay-tax-automation/commit/82ca6b24628abb49a08a52abf4c49e130b9fd139): Add automatic captcha solving with Capsolver API integration for seamless authentication without manual intervention.
- [`12a2f820`](https://github.com/stitch-05/paraguay-tax-automation/commit/12a2f8206ec851509abc474bb64e0b74a7519dc2): Add cron job configuration examples and refactor code for improved reusability of login and session management.
- [`d01fb0a3`](https://github.com/stitch-05/paraguay-tax-automation/commit/d01fb0a3548d2e50b44721d91bb3cf84915b3698): Add bug report template for standardized issue submissions.
- [`7fad868d`](https://github.com/stitch-05/paraguay-tax-automation/commit/7fad868da44f26e0891f5ed5b6a94827cbb067be): Major rewrite from bash to Python for improved maintainability and automated tax filing automation for Paraguay.

### Bug Fixes

- [`94bcee8e`](https://github.com/stitch-05/paraguay-tax-automation/commit/94bcee8e89095d23e1942c473a865501b7acd581): Fix response icon display on failure.
- [`f7d43778`](https://github.com/stitch-05/paraguay-tax-automation/commit/f7d43778aaf4835522d1d81e076c4e8493fb615c): Make NopeCHA instructions clearer for better user guidance.
- [`1512931`](https://github.com/stitch-05/paraguay-tax-automation/commit/15129313821c915f14e059c8f61c6aa1283e4ca0): Fix type issues for improved code reliability.
- [`f58cb976`](https://github.com/stitch-05/paraguay-tax-automation/commit/f58cb976bbb241e550cbd73c61bb11faaa8e42e7): Fix request delay calculation to ensure proper timing between HTTP requests.
- [`5a4777dc`](https://github.com/stitch-05/paraguay-tax-automation/commit/5a4777dc63f2257078c33a98a898fed0f60ff8d9): Fix captcha solver messages for better error reporting.
- [`533bb47f`](https://github.com/stitch-05/paraguay-tax-automation/commit/533bb47f895fa2a95074cebce4aa32fd40414b5f): Remove deprecated wget flags that caused installation issues.

### Documentation

- [`d300fdf4`](https://github.com/stitch-05/paraguay-tax-automation/commit/d300fdf4d63ee32a9bf51ca2ab9c5895b1abc2f1): Add Copilot instructions for AI-assisted development.
- [`b0db773f`](https://github.com/stitch-05/paraguay-tax-automation/commit/b0db773f77ec770bccc600d82281de288060ce8d): Add CLAUDE.md with Claude Code guidance and coding assistant best practices.
- [`c67556e2`](https://github.com/stitch-05/paraguay-tax-automation/commit/c67556e27cbe0726fac2f0436c045ce7565697d9): Update project details and metadata.
- [`ebed74c0`](https://github.com/stitch-05/paraguay-tax-automation/commit/ebed74c01ac8e58cb0172be02435d8ede0d467ca): Add AI skill documentation for automated task handling.
