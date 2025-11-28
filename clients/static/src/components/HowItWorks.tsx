import { Calendar, Truck, Check } from "lucide-react";

const steps = [
  {
    icon: Calendar,
    title: "Schedule",
    description: "Book a pickup in seconds through our app or website.",
  },
  {
    icon: Truck,
    title: "We collect",
    description: "Our team arrives at your door ready to handle your waste.",
  },
  {
    icon: Check,
    title: "Done",
    description: "Enjoy your clutter-free space. We handle the rest.",
  },
];

const HowItWorks = () => {
  return (
    <section className="py-32 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-20">
          <div className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
            How it works
          </div>
          <h2 className="text-5xl md:text-6xl font-bold mb-6">Simple by design</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Three steps to a cleaner space
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-12 max-w-5xl mx-auto">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 mb-6 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <step.icon className="w-8 h-8 text-primary" strokeWidth={1.5} />
                </div>
                <div className="text-sm font-medium text-primary mb-3">Step {index + 1}</div>
                <h3 className="text-2xl font-bold mb-3">{step.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-8 left-[60%] w-[80%] h-px bg-border" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
