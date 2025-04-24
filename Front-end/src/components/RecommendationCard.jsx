import React from 'react';
import PropTypes from 'prop-types';
import { Star, ThumbsUp, Share2, BookmarkPlus } from 'lucide-react';

export function RecommendationCard({ recommendation }) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden transform transition-all duration-300 hover:scale-105 hover:shadow-xl">
      {recommendation.imageUrl && (
        <div className="relative group">
          <img
            src={recommendation.imageUrl}
            alt={recommendation.title}
            className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-110"
          />
          <div className="absolute top-2 right-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gradient-to-r from-blue-500 to-blue-600 text-white transform transition-transform duration-300 hover:scale-105">
              {recommendation.category}
            </span>
          </div>
          {recommendation.trending && (
            <div className="absolute top-2 left-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gradient-to-r from-red-500 to-pink-500 text-white animate-pulse">
                Trending
              </span>
            </div>
          )}
        </div>
      )}
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-1 group-hover:text-blue-600 transition-colors duration-300">
            {recommendation.title}
          </h3>
          <div className="flex items-center">
            <Star className="h-5 w-5 text-yellow-400 fill-current animate-pulse" />
            <span className="ml-1 text-sm text-gray-600">{recommendation.rating}</span>
          </div>
        </div>
        <p className="mt-2 text-sm text-gray-600 line-clamp-2 group-hover:text-gray-900 transition-colors duration-300">
          {recommendation.description}
        </p>
        <div className="mt-4 flex items-center justify-between">
          <div className="flex space-x-2">
            <button className="p-2 hover:bg-blue-50 rounded-full transition-all duration-300 transform hover:scale-110 group">
              <ThumbsUp className="h-5 w-5 text-gray-600 group-hover:text-blue-600 transition-colors duration-300" />
            </button>
            <button className="p-2 hover:bg-green-50 rounded-full transition-all duration-300 transform hover:scale-110 group">
              <Share2 className="h-5 w-5 text-gray-600 group-hover:text-green-600 transition-colors duration-300" />
            </button>
            <button className="p-2 hover:bg-purple-50 rounded-full transition-all duration-300 transform hover:scale-110 group">
              <BookmarkPlus className="h-5 w-5 text-gray-600 group-hover:text-purple-600 transition-colors duration-300" />
            </button>
          </div>
          <span className="text-xs text-gray-500 italic">
            {new Date(recommendation.timestamp).toLocaleDateString('fr-FR', {
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })}
          </span>
        </div>
      </div>
    </div>
  );
}

RecommendationCard.propTypes = {
  recommendation: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    category: PropTypes.string.isRequired,
    rating: PropTypes.number.isRequired,
    imageUrl: PropTypes.string,
    timestamp: PropTypes.string.isRequired,
    trending: PropTypes.bool
  }).isRequired
};