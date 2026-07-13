# NyanwTools 

This document has higher priority than AI assumptions.

When there is a conflict between your own design ideas and this document, always follow this document.

## Overview

NyanwTools is a Blender 5.0.0 addon created specifically to speed up the creation of VTuber blendshapes.

The addon is intended for a production workflow where many avatars are created repeatedly. Every feature should remove repetitive manual work rather than introduce new workflows.

The primary goal of the addon is to reduce the amount of repetitive clicks required to prepare an avatar.

This addon is not intended to be a universal Shape Key addon.

It is designed around VTuber production.

---

# Design Philosophy

The addon should remain:

- Fast
- Simple
- Predictable

Every feature should be understandable in one sentence.

Avoid unnecessary settings.

Avoid automatic actions unless explicitly requested by the user.

The addon should feel like a native Blender tool.

---

# Blender Version

Target Blender version:

5.0.0

Compatibility with older versions is not required.

---

# Addon Name

NyanwTools

Author:

NyanWake

---

# Project Structure

The project is divided into small modules.

ui.py

    User Interface only.

operators.py

    Blender Operators.

presets.py

    Blendshape preset definitions.

mirror.py

    Mirror related functions.

derived.py

    Functions that create new Blendshapes from existing Blendshapes.

No business logic should exist inside ui.py.

---

# Main Features

The addon consists of three major systems.

## 1. Blendshape Sets

Purpose:

Create standard Blendshape collections.

Initially supported:

- ARKit
- NyanWake Eyes
- VRChat Visemes
- MMD English
- MMD Japanese

The user selects one or more Blendshape families.

Pressing

Create Blendshapes

creates every missing Blendshape.

Existing Blendshapes are never recreated.

---

Each family has a status.

Green

All Blendshapes exist.

Yellow

Some Blendshapes exist.

Red

None exist.

Status is calculated automatically.

---

Blendshape families are expandable.

When expanded they display every Blendshape together with its current status.

---

Families may optionally define a separator.

Example:

separator = "Eyes"

When Create Blendshapes is executed the addon creates

════ Eyes ════

before creating Blendshapes belonging to that section.

Separators are also only created once.

Separator formatting is handled by code.

Preset files only store the separator title.

---

## 2. Mirror Blendshape

Purpose:

Duplicate a completed Left or Right Blendshape to its opposite side.

Workflow:

Select Blendshape

↓

Press

Flip Selected Blendshape

The addon automatically

- detects Left / Right pair
- creates the opposite Blendshape if necessary
- copies the Blendshape
- executes Blender's built-in Blendshape Flip

The addon should use Blender's native Flip functionality.

No custom mirror algorithm should be implemented.

---

## 3. Combine Blendshapes

Purpose:

Create a new Blendshape from the current Blendshape mix.

Workflow:

User selects destination Blendshape.

User adjusts existing Blendshapes until the desired facial expression is achieved.

User presses

Combine Blendshape to Selected

The addon creates a new Blendshape using Blender's native

New Shape From Mix

The addon is not limited to MMD.

This system should work for any future Blendshape preset.

---

# Presets

Preset data should contain only data.

Never UI state.

Never calculated values.

Never status.

Each preset contains

- Name
- Optional separator
- Blendshape list

Nothing more.

---

# Icons

The addon uses custom icons.

Current icons:

logo.png

green.png

yellow.png

red.png

Status icons are determined by calculated Blendshape completion.

Icons are never defined by preset data.

---

# UI

The addon uses Blender's sidebar.

Category:

NyanwTools

Sections:

▼ Blendshape Sets

▼ Combine Blendshapes

Mirror is integrated into Blendshape Sets.

Mirror does not need its own section.

---

# Future Features

Possible future additions:

- Automatic MMD generation from ARKit
- Additional Blendshape presets
- Utility tools
- Export helpers

Future features should never complicate the primary workflow.

---

# Development Rules

Do not rewrite working systems without reason.

Prefer extending existing architecture.

Keep functions small.

Keep modules focused.

Avoid duplicated logic.

Every change should preserve the simplicity of the addon.

The user of this addon is an experienced VTuber creator, not a programmer.

The UI should therefore always prioritize usability over configurability.
