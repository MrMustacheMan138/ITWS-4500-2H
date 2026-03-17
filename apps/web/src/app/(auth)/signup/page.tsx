import Link from 'next/link';
import { SignUpForm } from '@/components/auth/SignUpForm';
import Header from '@/components/common/header';

export default function SignupPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header/>
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">
              Create Account
            </h1>
            <p className="mt-2 text-sm text-gray-600">
              Sign up to get started
            </p>
          </div>

          {/* Placeholder Card */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="text-gray-600">
              <SignUpForm/>
            </div>
          </div>

          {/* Login Link */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link
                href="/login"
                className="font-medium text-blue-600 hover:text-blue-700 hover:underline"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
