---
name: Clinical Intelligence System
colors:
  surface: '#f9f9ff'
  surface-dim: '#d7dae5'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f3ff'
  surface-container: '#ebedf9'
  surface-container-high: '#e5e8f3'
  surface-container-highest: '#dfe2ed'
  on-surface: '#181c23'
  on-surface-variant: '#434654'
  inverse-surface: '#2c3039'
  inverse-on-surface: '#eef0fc'
  outline: '#737685'
  outline-variant: '#c3c6d6'
  surface-tint: '#0c56d0'
  primary: '#003d9b'
  on-primary: '#ffffff'
  primary-container: '#0052cc'
  on-primary-container: '#c4d2ff'
  inverse-primary: '#b2c5ff'
  secondary: '#00677d'
  on-secondary: '#ffffff'
  secondary-container: '#50d9fe'
  on-secondary-container: '#005c70'
  tertiary: '#324749'
  on-tertiary: '#ffffff'
  tertiary-container: '#495e61'
  on-tertiary-container: '#c0d7da'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2ff'
  primary-fixed-dim: '#b2c5ff'
  on-primary-fixed: '#001848'
  on-primary-fixed-variant: '#0040a2'
  secondary-fixed: '#b3ebff'
  secondary-fixed-dim: '#4cd6fb'
  on-secondary-fixed: '#001f27'
  on-secondary-fixed-variant: '#004e5f'
  tertiary-fixed: '#d0e7ea'
  tertiary-fixed-dim: '#b4cbce'
  on-tertiary-fixed: '#091f21'
  on-tertiary-fixed-variant: '#364a4d'
  background: '#f9f9ff'
  on-background: '#181c23'
  surface-variant: '#dfe2ed'
typography:
  headline-xl:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-bold:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  transcript-mono:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '450'
    lineHeight: 26px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  margin-mobile: 16px
  margin-desktop: 32px
  gutter: 16px
  card-padding: 20px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is rooted in the "Clinical Modernism" aesthetic—a blend of high-utility **Corporate / Modern** structure with **Minimalist** clarity. It is designed to evoke a sense of absolute reliability, precision, and high-tech empathy. 

The target audience includes patients seeking immediate medical clarity and healthcare professionals requiring efficient AI-assisted triage. The visual language prioritizes "medical-grade" trust through generous whitespace, a strictly organized information hierarchy, and soft, approachable geometry. It avoids the coldness of traditional legacy medical software by using vibrant accent teals and subtle depth, mirroring the premium feel of Apple Health and modern telehealth leaders.

## Colors

The palette is anchored by **Deep Medical Blue** (#0052CC) to project authority and institutional trust. This is complemented by **Cyan Accents** (#00B4D8) used for interactive elements like voice recording waves and upload progress, signaling high-tech AI activity. 

**Clinical White** (#F8FAFC) serves as the primary canvas color to maintain a sterile, organized environment. Neutral tones are strictly cool-greys to prevent the UI from feeling "muddy." Use the **Soft Cyan** (#E0F7FA) as a background for informational callouts or AI-generated insights to distinguish them from standard patient data.

## Typography

This design system utilizes a dual-font approach. **Hanken Grotesk** is used for headlines to provide a sharp, contemporary "tech-first" feel. **Inter** is the workhorse for all body copy and clinical data, chosen for its exceptional legibility in dense medical contexts.

- **Headlines:** Use tight letter-spacing for large titles to maintain a cohesive visual block.
- **Transcripts:** AI-generated speech-to-text should use a slightly increased line height (26px) to improve readability during long consultations.
- **Labels:** Use uppercase for section headers (e.g., "YOUR MESSAGE") to provide clear visual separation between patient input and system output.

## Layout & Spacing

The layout follows a **fluid grid** model with a base-4 rhythm. On mobile devices, a 16px side margin is mandatory to ensure content does not feel cramped against the screen edges.

For desktop or tablet "Dashboard" views, use a centered fixed-width container (max-width: 1200px). Elements should be grouped into cards with a vertical stack spacing of 24px-32px to create clear mental "chapters" in the medical consultation flow. AI results should always occupy the primary (largest) column or be the terminal element in a vertical scroll.

## Elevation & Depth

Visual hierarchy is achieved through **Tonal Layers** and **Ambient Shadows**. 

1.  **Base Layer:** Clinical White (#F8FAFC).
2.  **Container Layer:** Pure White (#FFFFFF) cards. 
3.  **Shadows:** Use extremely soft, diffused shadows (0px 4px 20px rgba(0, 0, 0, 0.04)) to lift cards off the background without creating visual noise.
4.  **Active State:** Use a 1px border of Primary Blue (#0052CC) to indicate an active recording or a selected image, rather than increasing shadow depth.
5.  **AI Insights:** Use a subtle Inner Shadow or a Soft Cyan tint to give the "Doctor's Guidance" section a recessed, "focused" appearance.

## Shapes

The design system uses **Rounded** (Level 2) geometry. This 0.5rem (8px) base radius strikes a balance between professional precision and modern friendliness. 

- **Primary Buttons:** 8px radius.
- **Container Cards:** 16px (rounded-lg) for large consultation blocks.
- **Voice Pulse/Recording Buttons:** Pill-shaped (32px+) to encourage touch interaction.
- **Input Fields:** 8px radius with a light grey (1px) border.

## Components

### Buttons
- **Primary:** Solid Deep Blue with white text. Used for "Analyze Concern."
- **Secondary:** Clinical White with Blue border. Used for "Choose Files."
- **Destructive:** Soft Red background with Dark Red text for "Cancel" or "Delete."

### AI Analysis Card
- Contains a header with an "AI Specialist" icon, a transcript sub-section, and a "Doctor's Guidance" block. The guidance block should have a slightly different background tint (Soft Cyan) to distinguish AI-generated content from user-provided data.

### Voice Recorder
- A central circular button with a primary blue pulse animation. Below the button, a real-time waveform visualization in Cyan (#00B4D8) provides immediate feedback to the patient.

### Media Uploaders
- Empty states should feature dashed borders in a light neutral grey. Upon upload, thumbnails should have a small "remove" (x) icon in the top right and a progress bar if the file is large.

### Status Chips
- Small, rounded pills used for "HIPAA Compliant" or "Medical Grade Encryption" tags. Use a neutral grey background with a small shield icon to reinforce security.