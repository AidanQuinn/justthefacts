import { NextPageContext } from 'next';

interface ErrorProps {
  statusCode?: number;
  message?: string;
}

function Error({ statusCode, message }: ErrorProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          {statusCode || 'Error'}
        </h1>
        <p className="text-gray-600 mb-4">
          {message ||
           (statusCode === 404
             ? 'This page could not be found.'
             : 'An unexpected error has occurred.')}
        </p>
        <a
          href="/news"
          className="inline-block bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 transition-colors"
        >
          Go to News
        </a>
      </div>
    </div>
  );
}

Error.getInitialProps = ({ res, err }: NextPageContext) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404;
  const message = err?.message;
  return { statusCode, message };
};

export default Error;
