import logo from '../../assets/logo-erlangen.png';

const Navbar = () => {
  return (
    <header className="bg-primary text-primary-foreground p-4 shadow-md">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <img src={logo} alt="Erlangen Logo" className="h-10 w-auto" />
          <h1 className="text-xl font-semibold">Healthcare Dashboard</h1>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
