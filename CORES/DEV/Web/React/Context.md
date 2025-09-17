const ThemeCtx = React.createContext("light');

<ThemeCtx.Provicer value="dark">
  <ToolBar/>
</ThemeCtx.Provider>

<ThemeCtx.Consumer>
{value =>
</ThemeCtx.Consumer>

ThemedButton:
   static ctx = ThemeCtx;
   render() {
        return <Button theme={this.context} />
    }


