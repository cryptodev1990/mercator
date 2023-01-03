import { ToastProvider } from "react-toast-notifications";

type ContextType = {
  component: any;
  props?: any;
};

const contextProviders = [
  {
    component: ToastProvider,
    props: { autoDismiss: true },
  },
];

const ContextProviderNest = ({ children }: { children: React.ReactNode }) => {
  for (let i = contextProviders.length - 1; i >= 0; i--) {
    const ContextProvider = contextProviders[i];
    children = (
      <ContextProvider.component {...ContextProvider.props}>
        {children}
      </ContextProvider.component>
    );
  }
  return <>{children}</>;
};

export default ContextProviderNest;
