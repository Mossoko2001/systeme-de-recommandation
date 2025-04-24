import React from 'react';
import { Star, ThumbsUp, Share2, BookmarkPlus, X } from 'lucide-react';
import { supabase } from '../lib/supabase';

export function RecommendationDetail({ recommendation, onClose, user }) {
  const handleLike = async () => {
    if (!user) return;
    
    try {
      const { error } = await supabase
        .from('likes')
        .upsert({ 
          user_id: user.id,
          recommendation_id: recommendation.id
        });
      
      if (error) throw error;
    } catch (err) {
      console.error('Error liking recommendation:', err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full p-6 relative animate-[fadeIn_0.3s_ease-out]">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X className="h-6 w-6" />
        </button>

        <div className="flex flex-col md:flex-row gap-6">
          <div className="md:w-1/2">
            <img
              src={recommendation.imageUrl}
              alt={recommendation.title}
              className="w-full h-64 md:h-96 object-cover rounded-lg"
            />
          </div>

          <div className="md:w-1/2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">{recommendation.title}</h2>
              <div className="flex items-center">
                <Star className="h-5 w-5 text-yellow-400 fill-current" />
                <span className="ml-1 text-lg">{recommendation.rating}</span>
              </div>
            </div>

            <div className="mb-6">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {recommendation.category}
              </span>
              {recommendation.trending && (
                <span className="ml-2 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                  Trending
                </span>
              )}
            </div>

            <p className="text-gray-600 mb-6">{recommendation.description}</p>

            <div className="flex space-x-4">
              <button
                onClick={handleLike}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <ThumbsUp className="h-5 w-5" />
                <span>J'aime</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
                <Share2 className="h-5 w-5" />
                <span>Partager</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors">
                <BookmarkPlus className="h-5 w-5" />
                <span>Sauvegarder</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}