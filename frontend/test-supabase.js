import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://biwiswmrtwlazeqwlyac.supabase.co'
const supabaseKey = 'sb_publishable_WJWkERpNXPqdsvXxVmvpkw_4QqWR_im'
const supabase = createClient(supabaseUrl, supabaseKey)

async function testConnection() {
  console.log('Testing Supabase connection...')
  try {
    // A simple query to test connection (will return empty array or error if table doesn't exist, but won't fail connection)
    const { data, error } = await supabase.from('enquiry_analyses').select('*').limit(1)
    if (error && error.code !== '42P01') { // 42P01 is relation does not exist
      console.error('Connection failed:', error.message)
    } else {
      console.log('✅ Frontend successfully connected to Supabase!')
      if (error && error.code === '42P01') {
        console.log('Note: The table "enquiry_analyses" does not exist yet. This is expected if the backend has not run migrations.')
      }
    }
  } catch (err) {
    console.error('Connection error:', err)
  }
}

testConnection()