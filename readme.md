# NyanwTool

NyanwTool is a Blender addon that simplifies creating, organizing and managing Blendshapes for VTuber avatars.

I originally created this addon for my own workflow. As a VTuber avatar creator, I frequently build facial expressions for ARKit, VRChat and MMD, and wanted a faster way to create, organize and manage Shape Keys without constantly rearranging them by hand.

If you work with facial Blendshapes on a regular basis, I hope this tool saves you as much time as it saves me.

## Requirements

- Blender 5.0+

## Features

### Blendshape Presets

Built-in preset collections:

- Apple ARKit
- NyanWake Eyes
- VRChat Visemes
- MMD English
- MMD Japanese

*You can add them in the file. presets.py*

Each preset displays its completion status:

🟢 Complete

🟡 Partially complete

🔴 Missing

---

### Selection

- Click to select a single Blendshape.
- Click the selected Blendshape again to clear the selection.
- **Ctrl + Click** to select multiple Blendshapes.
- Click a preset header to select or deselect the entire family.

---

### Create Blendshapes

Creates only the missing Blendshapes from the current selection.

Existing Shape Keys are never duplicated.

New Blendshapes are automatically sorted into the correct order defined by the preset, while custom user Shape Keys remain below them.

---

### Flip Blendshape

Mirrors the selected Blendshape to its opposite side.

Supported naming conventions include:

- Left / Right
- _L / _R
- .L / .R

The opposite Shape Key is created automatically if it does not already exist.

**Known limitation**

Flip changes the active Shape Key position in Blender's Shape Key list.

This does not affect the addon itself and is planned to be fixed in a future update.

To avoid this behavior, select the **Basis** Shape Key before using **Flip**.

---

### Combine Blendshape

Creates a new Shape Key from the current deformation mix.

Behavior depends on the current selection:

- **No Blendshape selected**
  - Creates a new Blendshape and asks for its name.

- **One Blendshape selected**
  - Asks for confirmation before replacing the selected Blendshape with the current deformation mix.

- **Multiple Blendshapes selected**
  - Operation is cancelled to prevent accidental replacement.

This workflow is useful for creating expressions such as MMD Shape Keys from existing ARKit expressions.

---

## Current Version

**v1.1.0**

### Included

- Preset-based Blendshape management
- Status indicators
- Multi-selection
- Automatic Blendshape creation
- Automatic Shape Key sorting
- Blendshape mirroring
- Combine Blendshape workflow
- Custom icons
- VRM 1.0 Expressions preset
- VRCFaceTracking Unified Expressions preset
- Native Shape Keys Flip and Combine workflow

---

## Installation

1. Download the latest release.
2. Open **Edit → Preferences → Add-ons**.
3. Click **Install...**
4. Select the downloaded ZIP archive.
5. Enable **NyanwTool**.

---

## License

MIT License
