// src/config/supabase.js
// Supabase client — used for Auth and Storage uploads.

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY in your .env file.'
  )
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

/**
 * Upload a file to the "rv-fitness" Supabase Storage bucket.
 * Returns the public URL of the uploaded file.
 *
 * @param {File} file  - File object from an <input type="file">
 * @param {string} folder - Folder inside the bucket, e.g. "members", "events"
 * @returns {Promise<string>} public URL
 */
export async function uploadFile(file, folder = 'misc') {
  const ext = file.name.split('.').pop()
  const filename = `${folder}/${Date.now()}-${Math.random().toString(36).slice(2)}.${ext}`

  const { error } = await supabase.storage
    .from('rv-fitness')
    .upload(filename, file, { upsert: true })

  if (error) throw new Error(error.message)

  const { data } = supabase.storage.from('rv-fitness').getPublicUrl(filename)
  return data.publicUrl
}
