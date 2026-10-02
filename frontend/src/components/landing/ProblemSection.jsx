import React from 'react';
import { Eye, AlertTriangle, Navigation, QrCode, CheckCircle2 } from 'lucide-react';

export const ProblemSection = () => {
  const problemCards = [
    {
      title: "Supply Chain Visibility",
      icon: Eye,
      description: "Connect isolated operational silos across farmers, centers, and distributors into a unified view.",
      points: [
        "Unifies fragmented stakeholder records",
        "Tracks produce handoffs in real time",
        "Eliminates informational blackouts"
      ]
    },
    {
      title: "Inventory & Spoilage",
      icon: AlertTriangle,
      description: "Proactively monitor shelf-life degradation and temperature sensitive batches before loss occurs.",
      points: [
        "Identifies high-risk perishable batches",
        "Monitors storage environmental conditions",
        "Reduces unexpected warehouse decay"
      ]
    },
    {
      title: "Transportation Efficiency",
      icon: Navigation,
      description: "Optimize delivery dispatch routes to minimize transit duration and maintain cold-chain integrity.",
      points: [
        "Calculates multi-stop vehicle routes",
        "Minimizes transit delays & bottlenecks",
        "Ensures timely market delivery"
      ]
    },
    {
      title: "Product Traceability",
      icon: QrCode,
      description: "Establish transparent item provenance from origin harvest date to final consumer purchase.",
      points: [
        "Instant serial QR batch lookup",
        "Full origin harvest transparency",
        "Verifiable quality credentials"
      ]
    }
  ];

  return (
    <section className="py-20 bg-slate-900 text-white border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <span className="text-xs font-bold uppercase tracking-widest text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
            Agricultural Challenges Resolved
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            From Farm to Consumer, Every Step Matters
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            Traditional agricultural supply chains face fragmented communication, inventory blind spots, spoilage risk, routing inefficiencies, demand uncertainty, and missing provenance. AgroFlow AI unifies these critical operations into one intelligent system.
          </p>
        </div>

        {/* 4 Clean Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {problemCards.map((card) => {
            const IconComponent = card.icon;
            return (
              <div
                key={card.title}
                className="bg-slate-950/80 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/40 transition-all duration-300 flex flex-col justify-between shadow-lg"
              >
                <div>
                  <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-5">
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{card.title}</h3>
                  <p className="text-slate-400 text-xs leading-relaxed mb-4">
                    {card.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-800/80 space-y-2">
                  {card.points.map((point) => (
                    <div key={point} className="flex items-start gap-2 text-xs text-slate-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{point}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};
