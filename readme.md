# NyanwTool

**Save time while creating Blendshapes for VTuber/VRchat avatars in Blender.**

NyanwTool is a Blender addon designed to automate repetitive Shape Key setup for ARKit, VRChat, VRM and MMD workflows.

I originally created this addon for my own workflow. As a VTuber avatar creator, I constantly found myself creating the same Blendshape sets, organizing them into the correct order and repeating the same tasks on every new avatar.

NyanwTool automates those repetitive steps, letting you spend more time creating expressions instead of managing Shape Keys.

---

## Requirements

- Blender 5.0+ (Maybe on 4.2+)

---

## Workflow

NyanwTool follows Blender's native Shape Key workflow.

- Use **NyanwTool** side panel to generate missing Blendshapes from supported preset collections.
- Continue editing directly inside Blender's standard **Shape Keys** panel using the integrated **Flip** and **Combine** buttons.

This keeps Blender's default workflow intact while dramatically reducing repetitive setup work.

---

# Features

## Blendshape Presets

Built-in preset collections:

- Apple ARKit
- NyanWake Eyes
- VRChat Visemes
- VRM 1.0 Expressions
- VRCFaceTracking Unified Expressions
- MMD English
- MMD Japanese

*Additional preset collections can easily be created by editing `presets.py`.*

Each preset displays its current completion status:

🟢 Complete

🟡 Partially Complete

🔴 Missing

---

## Create Missing Blendshapes

Creates only the missing Blendshapes from the current selection.

Existing Shape Keys are never duplicated.

New Blendshapes are automatically sorted into the correct order defined by the preset while custom user Shape Keys remain below them.

This allows partially completed Blendshape sets to be safely completed without affecting existing work.

---

## Flip Blendshape

Located directly inside Blender's **Shape Keys** panel.

If you've created **eyeBlinkLeft** and want an identical **eyeBlinkRight**, simply press **Flip Blendshape**.

The addon automatically finds the matching Shape Key using common naming conventions:

- Left / Right
- _L / _R
- .L / .R

It then mirrors the deformation onto the matching Shape Key, or creates it automatically if it doesn't exist yet.

---

## Combine Blendshape

Located directly inside Blender's **Shape Keys** panel.

Create a new Shape Key from the current facial expression in a single click.

If **Basis** is selected, Combine creates a new Shape Key and asks for its name.

If another Shape Key is selected, Combine lets you quickly replace it with the current facial expression after confirmation.

This is especially useful when creating new expressions from existing Blendshape combinations without manually recreating them.

---

# Installation

1. Download the latest release.
2. Open **Edit → Preferences → Add-ons**.
3. Click **Install...**
4. Select the downloaded ZIP archive.
5. Enable **NyanwTool**.

---

# FAQ

### Flip doesn't mirror correctly

The most common cause is asymmetrical mesh topology.

In **Edit Mode**:

1. Select all vertices (**A**).
2. Go to **Mesh → Snap → Snap to Symmetry**.
3. Try using **Flip** again.

This usually fixes meshes whose left and right vertices are no longer perfectly symmetrical.

---

### Can I add my own preset collections?

Yes.

Simply edit `presets.py` and define your own Blendshape families.

---

### Does Flip only work with preset Blendshapes?

No.

Flip and Combine work with **any Shape Key**, even if it is not part of any preset collection.

---

# License

MIT License
