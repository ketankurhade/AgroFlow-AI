import React from 'react';
import { LandingNavbar } from '../components/landing/LandingNavbar';
import { LandingHero } from '../components/landing/LandingHero';
import { ProblemSection } from '../components/landing/ProblemSection';
import { HowItWorksSection } from '../components/landing/HowItWorksSection';
import { AiIntelligenceSection } from '../components/landing/AiIntelligenceSection';
import { DecisionCycleSection } from '../components/landing/DecisionCycleSection';
import { QrTraceabilitySection } from '../components/landing/QrTraceabilitySection';
import { PlatformRolesSection } from '../components/landing/PlatformRolesSection';
import { FinalCtaSection } from '../components/landing/FinalCtaSection';
import { LandingFooter } from '../components/landing/LandingFooter';

export const LandingPage = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-emerald-500 selection:text-white overflow-x-hidden">
      <LandingNavbar />
      <main>
        <LandingHero />
        <ProblemSection />
        <HowItWorksSection />
        <AiIntelligenceSection />
        <DecisionCycleSection />
        <QrTraceabilitySection />
        <PlatformRolesSection />
        <FinalCtaSection />
      </main>
      <LandingFooter />
    </div>
  );
};

export default LandingPage;
