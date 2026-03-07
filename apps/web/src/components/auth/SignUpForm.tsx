'use client';

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { signup } from '@/lib/api/endpoints';
import { signupSchema, type SignupFormData } from '@/lib/schema/auth';

export function SignUpForm() {
   const router = useRouter();
   const [formData, setFormData] = useState<SignupFormData>({
      name: '',
      email: '',
      password: '',
      confirmPassword: ''
   });
   const [errors, setErrors] = useState<Partial<Record<keyof SignupFormData, string>>>({});
   const [isLoading, setIsLoading] = useState(false);
   const [apiError, setApiError] = useState<string>('');

   const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setFormData((prev) => ({ ...prev, [name]: value }));
      // Clear error for this field
      setErrors((prev) => ({ ...prev, [name]: '' }));
      setApiError('');
   };

   const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      setErrors({});
      setApiError('');
   
      // Validate form data
      const result = signupSchema.safeParse(formData);
      if (!result.success) {
         const fieldErrors: Partial<Record<keyof SignupFormData, string>> = {};
         result.error.errors.forEach((err) => {
           if (err.path[0]) {
             fieldErrors[err.path[0] as keyof SignupFormData] = err.message;
           }
         });
         setErrors(fieldErrors);
         return;
      }
   
      setIsLoading(true);
   
      try {
         // Signup endpoint
         const response = await fetch('/api/auth/register', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify(formData),
         });
   
         if (!response.ok) {
            const data = await response.json();
            setApiError(data.message || 'Something went wrong. Please try again.');
         } else {
            router.push('/login'); // Redirect to login page after successful sign-up
            // NOTE: might change to re-direct to landing page and signed into session in the future
            router.refresh();
         } 
      } catch (error) {
         setApiError (
            error instanceof Error ? error.message : 'An unexpected error occured. Please try again'
         );
      } finally {
         setIsLoading(false);
      }
   };

   return (
      <form onSubmit={handleSubmit} className='space-y-6'>
         {/* Name Field */}
         <div>
            <label htmlFor='name' className='block text-sm font-medium text-gray-700 mb-2'> 
               Name 
            </label>
            <input
               id='name'
               name='name'
               type='text'
               autoComplete='name'
               value={formData.name}
               onChange={handleChange}
               disabled={isLoading}
               className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
               placeholder='user123'
            />
            {errors.name && (
               <p className='mt-1 text-sm text-red-600'>{errors.name}</p>
            )}
         </div>

         {/* Email Field */}
         <div>
            <label htmlFor='email' className='block text-sm font-medium text-gray-700 mb-2'>
               Email Address
            </label>
            <input
               id="email"
               name="email"
               type='email'
               autoComplete='email'
               value={formData.email}
               onChange={handleChange}
               disabled={isLoading}
               className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}  
               placeholder='you@example.com'
            />
            {errors.email && (
               <p className='mt-1 text-sm text-red-600'>{errors.email}</p>
            )} 
         </div>

         {/* Password Field */}
         <div>
            <label htmlFor='password' className='block text-sm font-medium text-gray-700 mb-2'>
               Password
            </label>
            <input
               id="password"
               name="password"
               type='password'
               autoComplete='current-password'
               value={formData.password}
               onChange={handleChange}
               disabled={isLoading}
               className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.password ? 'border-red-500' : 'border-gray-300'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}  
               placeholder='••••••••'
            />
            {errors.password && (
               <p className='mt-1 text-sm text-red-600'>{errors.password}</p>
            )} 
         </div>

         {/* Confirm Password Field */}
         <div>
            <label htmlFor='confirm-password' className='block text-sm font-medium text-gray-700 mb-2'>
               Confirm Password
            </label>
            <input
               id="confirmPassword"
               name="confirmPassword"
               type='confirmPassword'
               autoComplete='new-password'
               value={formData.confirmPassword}
               onChange={handleChange}
               disabled={isLoading}
               className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}  
               placeholder='••••••••'
            />
            {errors.confirmPassword && (
               <p className='mt-1 text-sm text-red-600'>{errors.confirmPassword}</p>
            )} 
         </div>

         {/* API Errors */}
         {apiError && (
         <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{apiError}</p>
         </div>
         )}
   

         {/* Submit Button */}
         <button
         type="submit"
         disabled={isLoading}
         className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
         >
         {isLoading ? (
            <span className="flex items-center justify-center">
               <svg
               className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
               xmlns="http://www.w3.org/2000/svg"
               fill="none"
               viewBox="0 0 24 24"
               >
               <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
               />
               <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
               />
               </svg>
               Signing up...
            </span>
         ) : (
            'Sign Up'
         )}
         </button>
      </form>
   );
}