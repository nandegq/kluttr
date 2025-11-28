import worker1 from "@/assets/worker-1.jpg";
import worker2 from "@/assets/worker-2.jpg";
import worker3 from "@/assets/worker-3.jpg";

const AnimatedBackground = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Worker - Floating from top left */}
      <div className="absolute top-[20%] -left-[10%] opacity-55 animate-float-slow">
        <img 
          src={worker1} 
          alt="" 
          className="w-[400px] h-[400px] object-cover rounded-2xl"
        />
      </div>
    </div>
  );
};

export default AnimatedBackground;
