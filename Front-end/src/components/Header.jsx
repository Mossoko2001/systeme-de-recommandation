import React, { useState } from 'react';
import { Menu, User, Bell, X, Home, Settings, LogOut, Phone, Info } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { AuthModal } from './AuthModal';

export function Header({ user, onSignOut }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showContact, setShowContact] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');

  const handleSignOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      onSignOut();
    } catch (err) {
      console.error('Error signing out:', err);
    }
  };

  const openAuthModal = (mode) => {
    setAuthMode(mode);
    setShowAuthModal(true);
    setShowUserMenu(false);
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    setShowNotifications(false);
    setShowUserMenu(false);
    setShowContact(false);
    setShowAbout(false);
  };

  const toggleNotifications = () => {
    setShowNotifications(!showNotifications);
    setShowUserMenu(false);
    setIsMenuOpen(false);
    setShowContact(false);
    setShowAbout(false);
  };

  const toggleUserMenu = () => {
    setShowUserMenu(!showUserMenu);
    setShowNotifications(false);
    setIsMenuOpen(false);
    setShowContact(false);
    setShowAbout(false);
  };

  const toggleContact = () => {
    setShowContact(!showContact);
    setShowUserMenu(false);
    setShowNotifications(false);
    setIsMenuOpen(false);
    setShowAbout(false);
  };

  const toggleAbout = () => {
    setShowAbout(!showAbout);
    setShowContact(false);
    setShowUserMenu(false);
    setShowNotifications(false);
    setIsMenuOpen(false);
  };

  return (
    <header className="bg-white shadow-sm relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <button
              onClick={toggleMenu}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors"
              aria-label="Menu principal"
            >
              {isMenuOpen ? (
                <X className="h-6 w-6 text-gray-600" />
              ) : (
                <Menu className="h-6 w-6 text-gray-600" />
              )}
            </button>
            <h1 className="ml-4 text-xl font-semibold text-gray-900">Système de Recommandation</h1>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleContact}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors"
              aria-label="Contact"
            >
              <Phone className="h-6 w-6 text-gray-600" />
            </button>
            <button
              onClick={toggleAbout}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors"
              aria-label="À propos"
            >
              <Info className="h-6 w-6 text-gray-600" />
            </button>
            <button
              onClick={toggleNotifications}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors relative"
              aria-label="Notifications"
            >
              <Bell className="h-6 w-6 text-gray-600" />
              <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full"></span>
            </button>
            <button
              onClick={toggleUserMenu}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors"
              aria-label="Menu utilisateur"
            >
              <User className="h-6 w-6 text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      {/* Menu latéral */}
      {isMenuOpen && (
        <div className="absolute top-16 left-0 w-64 bg-white shadow-lg rounded-br-lg z-50">
          <nav className="py-2">
            <button className="w-full px-4 py-2 flex items-center space-x-2 hover:bg-gray-100 transition-colors">
              <Home className="h-5 w-5 text-gray-600" />
              <span>Accueil</span>
            </button>
            <button className="w-full px-4 py-2 flex items-center space-x-2 hover:bg-gray-100 transition-colors">
              <Settings className="h-5 w-5 text-gray-600" />
              <span>Paramètres</span>
            </button>
          </nav>
        </div>
      )}

      {/* Menu Contact */}
      {showContact && (
        <div className="absolute top-16 right-16 w-96 bg-white shadow-lg rounded-lg z-50">
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-4">Contactez-nous</h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nom</label>
                <input type="text" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input type="email" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Message</label>
                <textarea rows="4" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"></textarea>
              </div>
              <button type="submit" className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
                Envoyer
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Menu À propos */}
      {showAbout && (
        <div className="absolute top-16 right-16 w-96 bg-white shadow-lg rounded-lg z-50">
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-4">À propos de nous</h3>
            <div className="space-y-4">
              <p className="text-gray-600">
                Notre système de recommandation utilise des algorithmes avancés d'intelligence artificielle pour vous proposer le contenu le plus pertinent en fonction de vos préférences et de votre historique de navigation.
              </p>
              <div className="border-t pt-4">
                <h4 className="font-medium text-lg mb-2">Notre Mission</h4>
                <p className="text-gray-600">
                  Améliorer l'expérience utilisateur en fournissant des recommandations personnalisées et pertinentes, tout en respectant la confidentialité des données.
                </p>
              </div>
              <div className="border-t pt-4">
                <h4 className="font-medium text-lg mb-2">Technologies Utilisées</h4>
                <ul className="list-disc list-inside text-gray-600">
                  <li>Intelligence Artificielle</li>
                  <li>Machine Learning</li>
                  <li>Analyse de données en temps réel</li>
                  <li>Sécurité des données avancée</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Menu notifications */}
      {showNotifications && (
        <div className="absolute top-16 right-16 w-80 bg-white shadow-lg rounded-lg z-50">
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-2">Notifications</h3>
            <div className="space-y-2">
              <div className="p-2 hover:bg-gray-50 rounded-md transition-colors">
                <p className="text-sm">Nouvelle recommandation disponible</p>
                <span className="text-xs text-gray-500">Il y a 5 minutes</span>
              </div>
              <div className="p-2 hover:bg-gray-50 rounded-md transition-colors">
                <p className="text-sm">Mise à jour du système</p>
                <span className="text-xs text-gray-500">Il y a 1 heure</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Menu utilisateur */}
      {showUserMenu && (
        <div className="absolute top-16 right-4 w-48 bg-white shadow-lg rounded-lg z-50">
          <div className="py-2">
            {user ? (
              <>
                <div className="px-4 py-2 border-b border-gray-200">
                  <p className="text-sm font-semibold">{user.email}</p>
                  <p className="text-xs text-gray-500">
                    {user.role === 'admin' ? 'Administrateur' : 'Utilisateur'}
                  </p>
                </div>
                <button
                  onClick={handleSignOut}
                  className="w-full px-4 py-2 flex items-center space-x-2 text-red-600 hover:bg-red-50 transition-colors"
                >
                  <LogOut className="h-5 w-5" />
                  <span>Déconnexion</span>
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => openAuthModal('login')}
                  className="w-full px-4 py-2 text-left hover:bg-gray-100"
                >
                  Se connecter
                </button>
                <button
                  onClick={() => openAuthModal('signup')}
                  className="w-full px-4 py-2 text-left hover:bg-gray-100"
                >
                  S'inscrire
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* Add AuthModal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        mode={authMode}
      />
    </header>
  );
}