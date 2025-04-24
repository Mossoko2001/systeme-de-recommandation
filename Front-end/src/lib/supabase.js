import { createClient } from '@supabase/supabase-js';

// Valeurs par défaut pour éviter les erreurs si les variables d'environnement ne sont pas définies
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://default-supabase-url.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'default-anon-key';

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Supabase URL and Anon Key are required');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);