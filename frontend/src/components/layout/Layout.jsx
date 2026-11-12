import Header from './Header';
import Footer from './Footer';

export default function Layout({ children }) {
  return <div className="min-h-screen"><Header /><div className="lg:pl-72"><main className="mx-auto w-full max-w-7xl px-5 py-7 sm:px-7 lg:px-10 lg:py-10">{children}</main><Footer /></div></div>;
}
