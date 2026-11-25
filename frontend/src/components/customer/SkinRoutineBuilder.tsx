import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Droplets, ShieldCheck, Sparkles, Sun } from 'lucide-react';
import { Badge, Card } from '@/components/common/UI';

type SkinTypeOption = 'dry' | 'oily' | 'combination' | 'sensitive' | 'normal';
type GoalOption = 'hydration' | 'glow' | 'balance' | 'uv-shield';

const SKIN_TYPES: Array<{ id: SkinTypeOption; label: string; summary: string }> = [
  { id: 'dry', label: 'Dry', summary: 'Rich ceramides & snail mucin layering' },
  { id: 'oily', label: 'Oily', summary: 'Lightweight gel textures & niacinamide' },
  { id: 'combination', label: 'Combination', summary: 'Balanced T-zone & barrier moisture' },
  { id: 'sensitive', label: 'Sensitive', summary: 'Soothing centella & heartleaf care' },
  { id: 'normal', label: 'Normal', summary: 'Daily radiance & preventative SPF' },
];

const GOALS: Array<{ id: GoalOption; label: string }> = [
  { id: 'hydration', label: 'Barrier Hydration' },
  { id: 'glow', label: 'Brightening & Glow' },
  { id: 'balance', label: 'Pore & Oil Balance' },
  { id: 'uv-shield', label: 'Daily UV Protection' },
];

const ROUTINE_PLANS: Record<
  SkinTypeOption,
  Record<
    GoalOption,
    { cleanse: string; treat: string; protect: string; finishTip: string }
  >
> = {
  dry: {
    hydration: {
      cleanse: 'Gentle Hydrating Cleanser',
      treat: 'Hyaluronic Serum + Snail 96 Mucin Essence',
      protect: 'Ceramide Barrier Cream & Birch Sun Cream',
      finishTip: 'Pair with cream or liquid blush for a dewy finish.',
    },
    glow: {
      cleanse: 'Soothing Gel Cleanser',
      treat: 'Glow Propolis Serum + Hyaluronic Acid',
      protect: 'Relief Sun SPF50+ & Illuminating Primer',
      finishTip: 'Opt for hydrating lip gloss or luminous satin foundation.',
    },
    balance: {
      cleanse: 'Low pH Gel Cleanser',
      treat: 'Dokdo Toner + Centella Ampoule',
      protect: 'Lightweight Moisture Cream + Fluid SPF',
      finishTip: 'Set only the T-zone lightly with finely milled powder.',
    },
    'uv-shield': {
      cleanse: 'Mild Morning Cleanser',
      treat: 'Dive-In Hyaluronic Serum',
      protect: 'Hyalu-Cica Water-Fit Sun Serum SPF50+',
      finishTip: 'Reapply with a non-tacky sun stick over makeup.',
    },
  },
  oily: {
    hydration: {
      cleanse: 'Foaming Facial Cleanser',
      treat: 'Heartleaf 77% Toner + Oil-Free Essence',
      protect: 'Weightless Gel Moisturizer + Matte Sun Stick',
      finishTip: 'Choose buildable matte or soft-focus foundation shades.',
    },
    glow: {
      cleanse: 'Low pH Good Morning Cleanser',
      treat: 'Niacinamide 10% + Zinc 1% Serum',
      protect: 'Invisible Fluid SPF50+',
      finishTip: 'Use matte setting powder under eyes and along the T-zone.',
    },
    balance: {
      cleanse: 'Foaming Cleanser',
      treat: 'Niacinamide + Heartleaf Soothing Toner',
      protect: 'Oil-Control Gel Cream + Matte Sun Stick',
      finishTip: 'Long-wear matte lip ink stays crisp all day.',
    },
    'uv-shield': {
      cleanse: 'Foaming Facial Cleanser',
      treat: 'Niacinamide Balancing Serum',
      protect: 'Anthelios Invisible Fluid + Matte Sun Stick',
      finishTip: 'Blotting before SPF touch-ups keeps shine controlled.',
    },
  },
  combination: {
    hydration: {
      cleanse: 'Balanced Low pH Cleanser',
      treat: 'Dokdo Toner + Dive-In Serum',
      protect: 'Soothing Gel-Cream + Relief Sun SPF50+',
      finishTip: 'Layer extra moisture only on dry cheek zones.',
    },
    glow: {
      cleanse: 'Low pH Gel Cleanser',
      treat: 'Glow Serum + Centella Ampoule',
      protect: 'Birch Juice Sun Cream SPF50+',
      finishTip: 'Liquid blush blends seamlessly over hydrated cheekbones.',
    },
    balance: {
      cleanse: 'Low pH Good Morning Cleanser',
      treat: 'Niacinamide 10% + Heartleaf Toner',
      protect: 'Barrier Lotion + Matte Sun Stick',
      finishTip: 'Natural-finish foundation adapts across dry and oily zones.',
    },
    'uv-shield': {
      cleanse: 'Gentle Gel Cleanser',
      treat: 'Centella Ampoule',
      protect: 'Relief Sun SPF50+ & Sun Stick Touch-Up',
      finishTip: 'Featherlight UV fluid wears cleanly under concealer.',
    },
  },
  sensitive: {
    hydration: {
      cleanse: 'Fragrance-Free Gentle Cleanser',
      treat: 'Centella Ampoule + Snail Mucin Essence',
      protect: 'Cicaplast Baume B5 + Mineral/Gentle SPF',
      finishTip: 'Patch-test new shades and keep active layers minimal.',
    },
    glow: {
      cleanse: 'Soothing Amino Cleanser',
      treat: 'Heartleaf 77% Toner + Centella Ampoule',
      protect: 'Calming Cream + Relief Sun SPF50+',
      finishTip: 'Sheer tinted lip balm adds color without irritation.',
    },
    balance: {
      cleanse: 'Low pH Soothing Cleanser',
      treat: 'Heartleaf 77% Soothing Toner',
      protect: 'Calming Gel Cream + Gentle Fluid SPF',
      finishTip: 'Avoid harsh physical scrubs; focus on barrier calm.',
    },
    'uv-shield': {
      cleanse: 'Mild Morning Wash',
      treat: 'Centella Soothing Ampoule',
      protect: 'Anthelios Fluid / Relief Sun SPF50+',
      finishTip: 'Gentle UV filters shield reactive skin without heavy residue.',
    },
  },
  normal: {
    hydration: {
      cleanse: 'Daily Gentle Cleanser',
      treat: 'Dokdo Toner + Hyaluronic Serum',
      protect: 'Daily Moisture Cream + Relief Sun SPF50+',
      finishTip: 'Satin-finish base formulas preserve natural skin luminosity.',
    },
    glow: {
      cleanse: 'Low pH Cleanser',
      treat: 'Glow Serum + Snail 96 Mucin Essence',
      protect: 'Water-Fit Sun Serum SPF50+',
      finishTip: 'Pair peachy blush with sheer lip luminizer.',
    },
    balance: {
      cleanse: 'Balanced Gel Cleanser',
      treat: 'Dokdo Toner + Niacinamide Serum',
      protect: 'Daily Moisturizer + Invisible Fluid SPF',
      finishTip: 'Light dusting of translucent powder locks in shade wear.',
    },
    'uv-shield': {
      cleanse: 'Refreshing Gel Cleanser',
      treat: 'Antioxidant Glow Serum',
      protect: 'Relief Sun SPF50+ + Matte Sun Stick',
      finishTip: 'Consistent daily SPF keeps tone even across seasons.',
    },
  },
};

export const SkinRoutineBuilder: React.FC = () => {
  const [skinType, setSkinType] = useState<SkinTypeOption>('combination');
  const [goal, setGoal] = useState<GoalOption>('glow');

  const plan = ROUTINE_PLANS[skinType][goal];

  return (
    <section
      id="skin-routine-builder"
      aria-labelledby="routine-builder-heading"
      className="relative overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-beige via-card to-blush/50 p-6 shadow-sm sm:p-10"
    >
      <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className="space-y-6">
          <div className="space-y-2">
            <Badge tone="blush">Personalized Ritual Quiz</Badge>
            <h2 id="routine-builder-heading" className="font-serif text-3xl font-bold sm:text-4xl">
              Build Your Skin-Type Routine
            </h2>
            <p className="text-sm leading-relaxed text-muted-fg">
              Select your skin profile and priority goal to preview a curated 3-step cosmetic
              ritual and jump straight to compatible formulas.
            </p>
          </div>

          <div className="space-y-3">
            <div className="text-xs font-semibold uppercase tracking-wider text-muted-fg">
              1. Select Your Skin Type
            </div>
            <div className="flex flex-wrap gap-2">
              {SKIN_TYPES.map((item) => {
                const active = skinType === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    aria-pressed={active}
                    onClick={() => setSkinType(item.id)}
                    className={`touch-target cursor-pointer rounded-lg border px-4 py-2 text-sm font-medium transition-colors duration-200 ${
                      active
                        ? 'border-primary bg-primary text-primary-fg shadow-sm'
                        : 'border-border bg-card text-foreground hover:bg-muted/60'
                    }`}
                  >
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="space-y-3">
            <div className="text-xs font-semibold uppercase tracking-wider text-muted-fg">
              2. Choose Primary Focus
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {GOALS.map((item) => {
                const active = goal === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    aria-pressed={active}
                    onClick={() => setGoal(item.id)}
                    className={`touch-target cursor-pointer rounded-lg border px-4 py-2.5 text-left text-sm font-medium transition-colors duration-200 ${
                      active
                        ? 'border-accent bg-accent text-accent-fg shadow-sm'
                        : 'border-border bg-card text-foreground hover:bg-muted/60'
                    }`}
                  >
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <Card className="border-card/80 bg-card/85 backdrop-blur-md shadow-md space-y-5">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-rose">
                Recommended 3-Step Ritual
              </div>
              <h3 className="font-serif text-2xl font-bold capitalize">
                {skinType} Skin · {GOALS.find((g) => g.id === goal)?.label}
              </h3>
            </div>
            <Sparkles className="h-6 w-6 text-accent" aria-hidden="true" />
          </div>

          <ol className="space-y-3 text-sm">
            <li className="flex items-start gap-3 rounded-lg bg-beige/60 p-3">
              <Droplets className="mt-0.5 h-5 w-5 shrink-0 text-primary" aria-hidden="true" />
              <div>
                <div className="text-xs font-semibold uppercase text-muted-fg">Step 01 · Cleanse</div>
                <div className="font-medium text-foreground">{plan.cleanse}</div>
              </div>
            </li>
            <li className="flex items-start gap-3 rounded-lg bg-blush/40 p-3">
              <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-rose" aria-hidden="true" />
              <div>
                <div className="text-xs font-semibold uppercase text-muted-fg">Step 02 · Treat</div>
                <div className="font-medium text-foreground">{plan.treat}</div>
              </div>
            </li>
            <li className="flex items-start gap-3 rounded-lg bg-beige/60 p-3">
              <Sun className="mt-0.5 h-5 w-5 shrink-0 text-accent" aria-hidden="true" />
              <div>
                <div className="text-xs font-semibold uppercase text-muted-fg">Step 03 · Protect</div>
                <div className="font-medium text-foreground">{plan.protect}</div>
              </div>
            </li>
          </ol>

          <p className="text-xs leading-relaxed text-muted-fg">
            <strong className="text-foreground">Makeup Pairing Tip:</strong> {plan.finishTip}
          </p>

          <Link
            to={`/catalog?skin_type=${skinType}`}
            className="touch-target inline-flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-fg transition-opacity duration-200 hover:opacity-90"
          >
            <span>Shop {skinType.charAt(0).toUpperCase() + skinType.slice(1)} Skin Formulas</span>
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </Card>
      </div>
    </section>
  );
};
