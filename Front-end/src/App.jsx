import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { RecommendationGrid } from './components/RecommendationGrid';
import { RecommendationDetail } from './components/RecommendationDetail';
import { Filter, Search, TrendingUp, Clock, Star } from 'lucide-react';
import { supabase } from './lib/supabase';

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeTab, setActiveTab] = useState('all');
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [user, setUser] = useState(null);
  const [darkMode, setDarkMode] = useState(false); // État pour le mode sombre

  useEffect(() => {
    // session pour récupérer l'utilisateur connecté
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    // écoute des changements d'état d'authentification
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Simulation de données de recommandations
  const mockRecommendations = [
    {
      id: '1',
      title: 'Machine Learning Fundamentals',
      description: 'Un cours complet sur les bases du machine learning et ses applications pratiques.',
      category: 'Education',
      rating: 4.8,
      imageUrl: 'https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg',
      timestamp: '2024-03-15T10:00:00Z',
      trending: true
    },
    {
      id: '2',
      title: 'Intelligence Artificielle Avancée',
      description: 'Découvrez les dernières avancées en IA et leurs impacts sur l\'industrie.',
      category: 'Technologie',
      rating: 4.5,
      imageUrl: 'https://images.pexels.com/photos/8386434/pexels-photo-8386434.jpeg',
      timestamp: '2024-03-14T15:30:00Z',
      trending: true
    },
    {
      id: '3',
      title: 'Data Science en Pratique',
      description: 'Applications concrètes de la data science dans différents secteurs.',
      category: 'Science',
      rating: 4.7,
      imageUrl: 'https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg',
      timestamp: '2024-03-13T09:15:00Z'
    },
    {
      id: '4',
      title: 'Cybersécurité pour Débutants',
      description: 'Apprenez les bases de la sécurité informatique et protégez vos données.',
      category: 'Technologie',
      rating: 4.6,
      imageUrl: 'https://images.pexels.com/photos/5380642/pexels-photo-5380642.jpeg',
      timestamp: '2024-03-12T14:20:00Z'
    },
    {
      id: '5',
      title: 'Développement Web Full Stack',
      description: 'Formation complète sur le développement web moderne.',
      category: 'Education',
      rating: 4.9,
      imageUrl: 'https://images.pexels.com/photos/574071/pexels-photo-574071.jpeg',
      timestamp: '2024-03-11T08:45:00Z',
      trending: true
    },
    {
      id: '6',
      title: 'Marketing Digital Avancé',
      description: 'Stratégies et techniques pour réussir votre présence en ligne.',
      category: 'Marketing',
      rating: 4.4,
      imageUrl: 'https://images.pexels.com/photos/905163/pexels-photo-905163.jpeg',
      timestamp: '2024-03-10T11:30:00Z'
    }
  ];

  useEffect(() => {
    // Simulation d'un appel API pour récupérer les recommandations
    setTimeout(() => {
      setRecommendations(mockRecommendations);
      setLoading(false);
    }, 1000);
  }, []);

  const getFilteredRecommendations = () => {
    let filtered = recommendations;

    if (activeTab === 'trending') {
      filtered = filtered.filter(rec => rec.trending);
    } else if (activeTab === 'recent') {
      filtered = [...filtered].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    } else if (activeTab === 'top') {
      filtered = [...filtered].sort((a, b) => b.rating - a.rating);
    }

    return filtered.filter(rec =>
      (selectedCategory === 'all' || rec.category === selectedCategory) &&
      (rec.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rec.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  const filteredRecommendations = getFilteredRecommendations();

  return (
    <div className={`${darkMode ? 'dark' : ''}`}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
        <Header user={user} onSignOut={() => setUser(null)} />
        <header className="p-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Recommandations</h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 dark:bg-blue-700"
          >
            {darkMode ? 'Mode Clair' : 'Mode Sombre'}
          </button>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Découvrez des Recommandations Personnalisées
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Notre système utilise l'intelligence artificielle pour vous proposer le contenu le plus pertinent.
            </p>
          </div>

          <div className="mb-8">
            <div className="flex flex-wrap gap-4 justify-center mb-6">
              <button
                onClick={() => setActiveTab('all')}
                className={`flex items-center px-4 py-2 rounded-full ${
                  activeTab === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                Tout
              </button>
              <button
                onClick={() => setActiveTab('trending')}
                className={`flex items-center px-4 py-2 rounded-full ${
                  activeTab === 'trending'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                Tendances
              </button>
              <button
                onClick={() => setActiveTab('recent')}
                className={`flex items-center px-4 py-2 rounded-full ${
                  activeTab === 'recent'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <Clock className="h-4 w-4 mr-2" />
                Récents
              </button>
              <button
                onClick={() => setActiveTab('top')}
                className={`flex items-center px-4 py-2 rounded-full ${
                  activeTab === 'top'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <Star className="h-4 w-4 mr-2" />
                Mieux notés
              </button>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 items-center">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 h-5 w-5" />
                <input
                  type="text"
                  placeholder="Rechercher des recommandations..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:focus:ring-blue-600"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="flex items-center gap-2">
                <Filter className="text-gray-400 dark:text-gray-500 h-5 w-5" />
                <select
                  className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:focus:ring-blue-600"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <option value="all">Toutes les catégories</option>
                  <option value="Education">Education</option>
                  <option value="Technologie">Technologie</option>
                  <option value="Science">Science</option>
                  <option value="Marketing">Marketing</option>
                </select>
              </div>
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-md p-4 text-red-700">
              {error}
            </div>
          ) : (
            <>
              {filteredRecommendations.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-600 dark:text-gray-300 text-lg">Aucune recommandation trouvée</p>
                </div>
              ) : (
                <RecommendationGrid recommendations={filteredRecommendations} />
              )}
            </>
          )}

          {selectedRecommendation && (
            <RecommendationDetail
              recommendation={selectedRecommendation}
              onClose={() => setSelectedRecommendation(null)}
              user={user}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;