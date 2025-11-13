const About = () => {
  return (
    <section id="about" className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-4xl font-bold text-gray-900 mb-6">About Our Project</h2>
            <p className="text-gray-600 mb-4">
              We're building a solution that addresses real-world problems with innovative technology. 
              Our fullstack approach ensures seamless integration and optimal performance.
            </p>
            <p className="text-gray-600 mb-6">
              Developed during the hackathon with passion and dedication, our project combines 
              cutting-edge frontend and backend technologies to deliver exceptional user experience.
            </p>
            <button className="text-indigo-600 font-semibold hover:text-indigo-700 flex items-center">
              Read More <ArrowRight className="ml-2" size={20} />
            </button>
          </div>
          <div className="bg-indigo-100 h-64 rounded-lg flex items-center justify-center">
            <span className="text-indigo-600 text-6xl">🚀</span>
          </div>
        </div>
      </div>
    </section>
  );
};