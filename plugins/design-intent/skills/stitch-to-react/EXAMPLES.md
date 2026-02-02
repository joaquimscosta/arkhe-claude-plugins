# Examples

Real-world examples of converting Google Stitch exports to React components.

---

## Example 1: Basic Component Conversion

### Input: Stitch Export

```
design-intent/google-stitch/dashboard/exports/
├── 01-metric-card.html
└── 01-metric-card.png
```

**Stitch HTML (simplified):**

```html
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          brand: '#3B82F6',
        },
      },
    },
  };
</script>
<div class="bg-white rounded-lg shadow-md p-6">
  <div class="flex items-center justify-between">
    <span class="text-gray-500 text-sm">Total Revenue</span>
    <span class="material-symbols-outlined text-brand">trending_up</span>
  </div>
  <div class="mt-2">
    <span class="text-3xl font-bold text-gray-900">$45,231</span>
    <span class="ml-2 text-sm text-green-500">+12.5%</span>
  </div>
</div>
```

### Context Check

```
Project Context:
- Design System: Fluent UI v9
- Existing patterns:
  - card-layout.md: 16px padding, tokens.shadow4
  - typography-scale.md: size 800 for headlines
```

### Conflict Detected

```
## Design Conflict

**Element**: Card shadow
**Stitch**: shadow-md (0 4px 6px rgba)
**Pattern**: tokens.shadow4

**Recommendation**: Use pattern - Fluent shadow tokens
```

### Generated Output

**tokens.ts:**

```ts
/**
 * Design tokens from Stitch metric-card export
 * Mapped to Fluent UI tokens where available
 */
import { tokens } from '@fluentui/react-components';

export const metricCardTokens = {
  // Colors - mapped to Fluent
  brand: tokens.colorBrandBackground,
  textPrimary: tokens.colorNeutralForeground1,
  textSecondary: tokens.colorNeutralForeground3,
  positive: tokens.colorPaletteGreenForeground1,

  // Spacing - from Stitch p-6 (24px)
  padding: tokens.spacingHorizontalXL,

  // Using pattern shadow instead of Stitch shadow-md
  shadow: tokens.shadow4,
} as const;
```

**types.ts:**

```ts
export interface MetricCardProps {
  label: string;
  value: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    percentage: string;
  };
  icon?: string;
}
```

**MetricCard.tsx:**

```tsx
/**
 * CUSTOM COMPONENT: MetricCard
 * Source: 01-metric-card.html
 * Base: @fluentui/react-components/Card
 * Reason: Custom metric display layout with trend indicator
 * Created: YYYY-MM-DD
 *
 * Original Reference: design-intent/google-stitch/dashboard/exports/01-metric-card.png
 */

import React from 'react';
import { Card, Text, tokens } from '@fluentui/react-components';
import { ArrowTrendingUp24Regular } from '@fluentui/react-icons';
import { metricCardTokens } from './tokens';
import type { MetricCardProps } from './types';

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  trend,
  icon,
}) => {
  return (
    <Card
      style={{
        padding: metricCardTokens.padding,
        boxShadow: metricCardTokens.shadow,
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <Text
          size={200}
          style={{ color: metricCardTokens.textSecondary }}
        >
          {label}
        </Text>
        <ArrowTrendingUp24Regular
          style={{ color: metricCardTokens.brand }}
        />
      </div>
      <div style={{ marginTop: tokens.spacingVerticalS }}>
        <Text size={800} weight="bold">
          {value}
        </Text>
        {trend && (
          <Text
            size={200}
            style={{
              marginLeft: tokens.spacingHorizontalS,
              color: trend.direction === 'up'
                ? metricCardTokens.positive
                : tokens.colorNeutralForeground3,
            }}
          >
            {trend.percentage}
          </Text>
        )}
      </div>
    </Card>
  );
};
```

---

## Example 2: Multi-State Button from Stitch

### Input: Stitch Export with Multiple States

```
design-intent/google-stitch/recording/exports/
├── 02-record-button.html
└── 02-record-button.png
```

The HTML shows a button with 6 visual states encoded in the markup.

### State Analysis

From Stitch HTML, identified states:
1. **Idle** - Default state, ready to record
2. **Hover** - Subtle highlight
3. **Recording** - Active, pulsing animation
4. **Paused** - Recording paused
5. **Processing** - Converting audio
6. **Error** - Recording failed

### Generated Output

**types.ts:**

```ts
export type RecordButtonState =
  | 'idle'
  | 'hover'
  | 'recording'
  | 'paused'
  | 'processing'
  | 'error';

export interface RecordButtonProps {
  state: RecordButtonState;
  onRecord: () => void;
  onPause: () => void;
  onStop: () => void;
  disabled?: boolean;
}
```

**RecordButton.styles.ts:**

```ts
/**
 * Styles extracted from Stitch 02-record-button.html
 * Custom keyframe animations preserved from source
 */
import { makeStyles, tokens } from '@fluentui/react-components';

export const useRecordButtonStyles = makeStyles({
  button: {
    width: '64px',
    height: '64px',
    borderRadius: '50%',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 200ms ease-out',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },

  idle: {
    backgroundColor: tokens.colorBrandBackground,
    ':hover': {
      backgroundColor: tokens.colorBrandBackgroundHover,
      transform: 'scale(1.05)',
    },
  },

  recording: {
    backgroundColor: tokens.colorPaletteRedBackground3,
    animationName: {
      '0%': { transform: 'scale(1)', opacity: 1 },
      '50%': { transform: 'scale(1.1)', opacity: 0.8 },
      '100%': { transform: 'scale(1)', opacity: 1 },
    },
    animationDuration: '1.5s',
    animationIterationCount: 'infinite',
  },

  paused: {
    backgroundColor: tokens.colorNeutralBackground4,
  },

  processing: {
    backgroundColor: tokens.colorNeutralBackground3,
    cursor: 'wait',
  },

  error: {
    backgroundColor: tokens.colorPaletteRedBackground1,
  },
});
```

**RecordButton.tsx:**

```tsx
/**
 * CUSTOM COMPONENT: RecordButton
 * Source: 02-record-button.html
 * Base: @fluentui/react-components/Button
 * Reason: Multi-state recording button with pulse animation
 * Created: YYYY-MM-DD
 *
 * Original Reference: design-intent/google-stitch/recording/exports/02-record-button.png
 */

import React from 'react';
import { mergeClasses } from '@fluentui/react-components';
import {
  Mic24Regular,
  Pause24Regular,
  Stop24Regular,
  Spinner24Regular,
  Warning24Regular,
} from '@fluentui/react-icons';
import { useRecordButtonStyles } from './RecordButton.styles';
import type { RecordButtonProps, RecordButtonState } from './types';

const stateIcons: Record<RecordButtonState, React.ReactNode> = {
  idle: <Mic24Regular />,
  hover: <Mic24Regular />,
  recording: <Stop24Regular />,
  paused: <Mic24Regular />,
  processing: <Spinner24Regular />,
  error: <Warning24Regular />,
};

export const RecordButton: React.FC<RecordButtonProps> = ({
  state,
  onRecord,
  onPause,
  onStop,
  disabled,
}) => {
  const styles = useRecordButtonStyles();

  const handleClick = () => {
    switch (state) {
      case 'idle':
      case 'paused':
        onRecord();
        break;
      case 'recording':
        onStop();
        break;
      default:
        break;
    }
  };

  return (
    <button
      className={mergeClasses(
        styles.button,
        styles[state]
      )}
      onClick={handleClick}
      disabled={disabled || state === 'processing'}
      aria-label={`Recording ${state}`}
    >
      {stateIcons[state]}
    </button>
  );
};
```

---

## Example 3: Full Layout Decomposition

### Input: Complex Layout Screen

```
design-intent/google-stitch/asr-interface/exports/
├── 01-layout-papia-asr.html
├── 01-layout-papia-asr.png
├── 02-header-nav.html
├── 02-header-nav.png
├── 03-recording-panel.html
└── 03-recording-panel.png
```

### Decomposition Strategy

```
01-layout-papia-asr.html (Full Screen)
├── Header (extract from 02-header-nav.html)
│   ├── Logo (atomic)
│   ├── Navigation (composite)
│   └── UserMenu (composite)
├── Main Content
│   ├── RecordingPanel (from 03-recording-panel.html)
│   │   ├── RecordButton (atomic, multi-state)
│   │   ├── WaveformDisplay (atomic)
│   │   └── TranscriptPreview (composite)
│   └── TranscriptionResults (composite)
└── Footer (atomic)
```

### Pattern Check Output

```
Project Context:
- Design System: Fluent UI v9
- Existing patterns:
  - header-layout.md: 64px height, horizontal nav
  - sidebar-layout.md: 240px width, collapsible
  - (No recording-related patterns exist)

New patterns to establish:
1. recording-panel-layout - Recording interface structure
2. waveform-display - Audio visualization styling
3. transcript-card - Transcription result display
```

### Generated File Structure

```
src/components/asr-interface/
├── index.ts
├── types.ts
├── tokens.ts
├── ASRLayout.tsx           # Main layout
├── Header/
│   ├── Header.tsx
│   ├── Logo.tsx
│   ├── Navigation.tsx
│   └── UserMenu.tsx
├── RecordingPanel/
│   ├── RecordingPanel.tsx
│   ├── RecordButton.tsx
│   ├── WaveformDisplay.tsx
│   └── TranscriptPreview.tsx
└── TranscriptionResults/
    ├── TranscriptionResults.tsx
    └── TranscriptCard.tsx
```

### Main Layout Component

```tsx
/**
 * ASR Interface Layout
 * Source: 01-layout-papia-asr.html
 * Composed from multiple Stitch screens
 *
 * Original Reference: design-intent/google-stitch/asr-interface/exports/01-layout-papia-asr.png
 */

import React from 'react';
import { tokens } from '@fluentui/react-components';
import { Header } from './Header/Header';
import { RecordingPanel } from './RecordingPanel/RecordingPanel';
import { TranscriptionResults } from './TranscriptionResults/TranscriptionResults';
import type { ASRLayoutProps } from './types';

export const ASRLayout: React.FC<ASRLayoutProps> = ({
  user,
  recordings,
  onRecord,
  onTranscribe,
}) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      backgroundColor: tokens.colorNeutralBackground2,
    }}>
      <Header user={user} />

      <main style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: '1fr 2fr',
        gap: tokens.spacingHorizontalXL,
        padding: tokens.spacingHorizontalXL,
      }}>
        <RecordingPanel
          onRecord={onRecord}
          onTranscribe={onTranscribe}
        />
        <TranscriptionResults recordings={recordings} />
      </main>
    </div>
  );
};
```

---

## Example 4: Handling Stitch Animations

### Input: Animated Component

Stitch HTML contains custom keyframe animation:

```html
<style>
  @keyframes slideIn {
    from {
      transform: translateX(-100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  .animate-slideIn {
    animation: slideIn 0.3s ease-out forwards;
  }
</style>
```

### Conversion to Fluent UI Styles

```tsx
import { makeStyles, shorthands } from '@fluentui/react-components';

export const useAnimatedPanelStyles = makeStyles({
  panel: {
    // Converted from Stitch @keyframes slideIn
    animationName: {
      from: {
        transform: 'translateX(-100%)',
        opacity: 0,
      },
      to: {
        transform: 'translateX(0)',
        opacity: 1,
      },
    },
    animationDuration: '0.3s',
    animationTimingFunction: 'ease-out',
    animationFillMode: 'forwards',
  },
});
```

---

## Example 5: Conflict Resolution Flow

### Scenario: Multiple Conflicts

```
## Design Conflicts Detected

### 1. Border Radius
**Stitch**: 4px (rounded)
**Pattern**: 8px (button-styling.md)
**Elements**: Buttons, cards, inputs

### 2. Primary Color
**Stitch**: #3B82F6 (Tailwind blue-500)
**Pattern**: #0078D4 (Fluent brand)
**Elements**: CTAs, links, focus rings

### 3. Shadow Depth
**Stitch**: shadow-lg (heavy)
**Pattern**: tokens.shadow4 (subtle)
**Elements**: Cards, modals
```

### User Response

```
1. Border Radius: Use pattern (8px) - maintain consistency
2. Primary Color: Use pattern (Fluent brand) - brand guidelines
3. Shadow Depth: Follow Stitch (shadow-lg) - want more depth
```

### Resulting tokens.ts

```ts
/**
 * Tokens resolved from Stitch export + pattern conflicts
 * Conflict resolutions documented inline
 */
import { tokens } from '@fluentui/react-components';

export const resolvedTokens = {
  // CONFLICT RESOLVED: Using pattern value
  // Stitch: 4px, Pattern: 8px
  // Decision: Pattern - maintain consistency
  borderRadius: tokens.borderRadiusMedium, // 8px

  // CONFLICT RESOLVED: Using pattern value
  // Stitch: #3B82F6, Pattern: #0078D4
  // Decision: Pattern - brand guidelines
  primaryColor: tokens.colorBrandBackground,

  // CONFLICT RESOLVED: Using Stitch value
  // Stitch: shadow-lg, Pattern: shadow4
  // Decision: Stitch - want more depth for this feature
  cardShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
} as const;
```

---

## Example 6: Pattern Suggestion Output

After successful conversion, suggest new patterns:

```markdown
## Patterns to Document

Based on this Stitch conversion, consider documenting:

### 1. recording-interface-layout.md
**Decision**: Two-column layout with recording controls left, results right
**Elements**: RecordingPanel, TranscriptionResults
**Breakpoint**: Stack vertically below 768px

### 2. multi-state-button.md
**Decision**: Circular buttons with state-based colors and animations
**Elements**: RecordButton, ProcessingIndicator
**States**: idle, active, processing, error

### 3. waveform-display.md
**Decision**: SVG-based waveform with gradient fill
**Elements**: WaveformDisplay
**Colors**: Brand gradient for active, neutral for inactive

Run `/save-patterns` to capture these patterns.
```
