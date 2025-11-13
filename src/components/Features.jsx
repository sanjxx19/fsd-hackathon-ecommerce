const Features = () => {
  const features = [
    {
      title: "Fast Performance",
      description: "Optimized for speed and efficiency with modern technologies.",
      icon: "⚡"
    },
    {
      title: "Secure & Reliable",
      description: "Enterprise-grade security with 99.9% uptime guarantee.",
      icon: "🔒"
    },
    {
      title: "Easy Integration",
      description: "Simple API and comprehensive documentation for quick setup.",
      icon: "🔧"
    },
    {
      title: "24/7 Support",
      description: "Round-the-clock customer support whenever you need help.",
      icon: "💬"
    }
  ];

  return (
    <section id="features" className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Features</h2>
          <p className="text-gray-600">Everything you need to succeed</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="p-6 border rounded-lg hover:shadow-lg transition">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};