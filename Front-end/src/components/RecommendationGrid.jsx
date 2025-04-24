import React from 'react';
import PropTypes from 'prop-types';
import { RecommendationCard } from './RecommendationCard';

export function RecommendationGrid({ recommendations }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 animate-[fadeIn_0.5s_ease-in]">
      {recommendations.map((recommendation, index) => (
        <div
          key={recommendation.id}
          className="opacity-0 animate-[fadeIn_0.5s_ease-in_forwards]"
          style={{ animationDelay: `${index * 0.1}s` }}
        >
          <RecommendationCard recommendation={recommendation} />
        </div>
      ))}
    </div>
  );
}

RecommendationGrid.propTypes = {
  recommendations: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      category: PropTypes.string.isRequired,
      rating: PropTypes.number.isRequired,
      imageUrl: PropTypes.string,
      timestamp: PropTypes.string.isRequired,
      trending: PropTypes.bool
    })
  ).isRequired
};