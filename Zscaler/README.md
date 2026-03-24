# Zscaler AutoPkg Recipes

This recipe is forked from an initial idea by @williamtheaker on Github to use the release notes to figure out new versions of Zscaler.

## Recipes

| Recipe | Description |
|--------|-------------|
| `Zscaler.download.recipe` | Downloads the latest Zscaler installer (.app.zip or .pkg) |
| `Zscaler.pkg.recipe` | Unzips the .app.zip and wraps it in a DMG (app workflow only) |
| `Zscaler.munki.recipe` | Imports the .app installer into Munki via DMG |
| `ZscalerPkg.munki.recipe` | Imports the .pkg installer directly into Munki |

## Input Variables

### Download options

| Variable | Default | Description |
|----------|---------|-------------|
| `DOWNLOAD_TYPE` | `app` | `app` for .app.zip, `pkg` for .pkg installer |
| `VERSION_PREFIX` | *(empty)* | Filter versions by prefix, e.g. `4.5` to pin to an LTS branch |
| `INCLUDE_LIMITED` | *(empty)* | Set to `True` to include limited availability (beta) releases |

### Munki options (Zscaler.munki.recipe only)

| Variable | Default | Description |
|----------|---------|-------------|
| `STRICT_ENFORCEMENT` | *(empty)* | Passed to the .app installbuilder |
| `POLICY_TOKEN` | *(empty)* | Passed to the .app installbuilder |
| `CLOUD_NAME` | *(empty)* | Passed to the .app installbuilder |
| `MODE` | *(empty)* | Passed to the .app installbuilder |
| `UNATT_MODE_UI` | *(empty)* | Passed to the .app installbuilder |

## Usage

### Default (latest version, .app.zip workflow via Munki)

```bash
autopkg run com.github.rickheil-recipes.munki.Zscaler
```

### Latest .pkg via Munki

```bash
autopkg run com.github.rickheil-recipes.munki.ZscalerPkg
```

### Pin to LTS branch (e.g. 4.5)

In your recipe override, set:

```xml
<key>Input</key>
<dict>
    <key>VERSION_PREFIX</key>
    <string>4.5</string>
</dict>
```

## Notes

- `INCLUDE_LIMITED` has been mostly unreliable in testing as the full versions are not published to the public CMS.
- The `ZscalerPkg.munki.recipe` inherits directly from the download recipe and skips the unarchive/DMG steps, so it does not support the installbuilder variables (`STRICT_ENFORCEMENT`, `POLICY_TOKEN`, etc.).
