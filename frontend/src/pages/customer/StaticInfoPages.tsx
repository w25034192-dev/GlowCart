import React from 'react';
import { Card } from '@/components/common/UI';

export const AboutPage: React.FC = () => (
  <Card className="mx-auto max-w-3xl space-y-4">
    <h1 className="font-serif text-3xl font-bold">About GlowCart</h1>
    <p className="text-sm leading-relaxed text-muted-fg">
      GlowCart is an international cosmetic e-commerce and batch-aware inventory platform built to
      demonstrate shade/volume variant selection, FEFO cosmetic expiry management, secure
      transaction processing, and real-time sales analytics.
    </p>
  </Card>
);

export const ContactPage: React.FC = () => (
  <Card className="mx-auto max-w-3xl space-y-4">
    <h1 className="font-serif text-3xl font-bold">Contact GlowCart</h1>
    <p className="text-sm text-muted-fg">
      Support Email: support@glowcart-demo.example · Hours: Mon–Fri, 09:00–18:00 UTC.
    </p>
  </Card>
);

export const PrivacyPolicyPage: React.FC = () => (
  <Card className="mx-auto max-w-3xl space-y-4">
    <h1 className="font-serif text-3xl font-bold">Privacy Policy</h1>
    <p className="text-sm text-muted-fg">
      GlowCart stores only account, address, and order records required for fulfillment. Payment card
      PAN and CVV numbers are never collected or persisted on GlowCart servers.
    </p>
  </Card>
);

export const TermsPage: React.FC = () => (
  <Card className="mx-auto max-w-3xl space-y-4">
    <h1 className="font-serif text-3xl font-bold">Terms &amp; Conditions</h1>
    <p className="text-sm text-muted-fg">
      Demo catalog items and USD prices are illustrative for academic demonstration purposes. Orders
      are subject to FEFO non-expired batch availability.
    </p>
  </Card>
);

