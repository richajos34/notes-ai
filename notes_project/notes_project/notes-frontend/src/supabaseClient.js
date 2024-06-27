// src/supabaseClient.js
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://mqkygzptkzpmrsyjjeyf.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xa3lnenB0a3pwbXJzeWpqZXlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTkzNjE2OTEsImV4cCI6MjAzNDkzNzY5MX0.yeKHh36VNcQw-i4GEwm2Ta8oGo6iXsb3lIoJO3rjugc';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
