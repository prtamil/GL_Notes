I created WTL code which uses WinRT/Cpp17 so i can combine COM/WinRT(not UWP) and WIN32 to create sysapps
so motto is 
**CombineAll Win32/Com/WinRT(native not uwp)**

### 1️⃣ C++/WinRT is **not inherently sandboxed**

- **C++/WinRT** is **just a C++ language projection of WinRT APIs**.
- **It does not force your app into an AppContainer**.
- You can write a **fully native desktop app** (Win32 / WTL / ATL style) using C++/WinRT to access modern Windows APIs.
- The **AppContainer sandbox only applies if you explicitly build a UWP or packaged WinRT app**.
    

> So: **C++/WinRT = fully native unless you target UWP/packaged sandbox**.

---

### 2️⃣ Win32 / COM / ATL / WTL

- These are **pure native frameworks**.
- They always have **full access to OS APIs**, memory, threads, etc.
- C++/WinRT can coexist with these; you can call WinRT APIs in a classic Win32 app without any restrictions.
    

---

### 3️⃣ .NET

- Managed runtime. Execution is **under CLR**.
- Native interop is possible, but your memory/threading is controlled by **GC and runtime**.
    

---

### ✅ Correct statement

- **C++/WinRT without UWP** → fully native, same privileges as Win32/ATL/WTL.
- **C++/WinRT in UWP / packaged app** → restricted by **AppContainer sandbox**.
- **.NET apps** → run on **managed runtime (CLR)**, sandboxed by runtime unless you P/Invoke.


|Technology / App Model|Language / Compiler|Runtime / Loader|Subsystem (PE)|Access / Privileges|Managed / Native|Notes|
|---|---|---|---|---|---|---|
|**Win32**|C/C++|Native PE → kernel loader|GUI / Console|Full OS access|Native|Classic Windows API|
|**ATL / WTL / COM**|C++|Native PE → kernel loader → COM runtime (if COM)|GUI / Console|Full OS access|Native|ATL/WTL are wrappers over Win32 / COM|
|**C++/WinRT (Desktop)**|C++17|Native PE → kernel loader → WinRT APIs|GUI / Console|Full OS access|Native|Uses modern WinRT APIs, fully native unless packaged as UWP|
|**C++/WinRT (UWP / AppContainer)**|C++17|Native PE → AppContainer → WinRT runtime|GUI|Restricted by AppContainer sandbox|Native|Sandboxed desktop / store app|
|**UWP / WinRT (C#/C++/XAML)**|C++ / C# / XAML|AppContainer → WinRT → OS|GUI|Restricted|Native|Store-sandboxed, limited OS access|
|**.NET (WinForms / WPF / Console)**|C# / VB.NET / F#|PE → CLR → JIT → managed execution|GUI / Console|Restricted by runtime|Managed|Full native interop via P/Invoke|


---

### 1️⃣ C++/WinRT on Win32 desktop

- **C++/WinRT** is **just a modern C++ projection for WinRT APIs**.
- You can freely create a **classic Win32 desktop app** (GUI, console, WTL, ATL, etc.) and use **all Win32 APIs**.
- Nothing stops you from mixing **C++17 features, Win32, ATL/WTL, and C++/WinRT APIs** in the same project.
    

---

### 2️⃣ Win32 APIs inside C++/WinRT app

- As long as your **app is a desktop app** (not a UWP / AppContainer app), you have **full access to Win32 APIs**.
- You can call `CreateWindowEx`, `GDI+`, `DirectX`, `COM` APIs, registry, filesystem — the full native stack.
- C++/WinRT headers are just **helpers over COM-based WinRT interfaces**; they don’t restrict access.
    

---

### 3️⃣ Things to watch out for

1. **AppContainer sandbox**
    - If you build a **UWP / packaged app**, then Win32 API access is **restricted by the sandbox**.
    - For desktop apps, no sandbox applies.
        
2. **Compiler / C++ version**
    
    - Use **C++17 or later** for C++/WinRT headers and modern language features.
    - Ensure you enable `/permissive-` and proper C++17 standard in your project settings.
        
3. **Linking / headers**
    
    - Add `#include <winrt/...>` for WinRT APIs.
    - Keep `C:\Program Files (x86)\Windows Kits\10\Include\<version>\cppwinrt` in **Include directories**.
    - Link necessary WinRT libraries (`WindowsApp.lib`) if required.
        

---

### ✅ TL;DR

> **Desktop C++/WinRT = fully native Win32 app + modern WinRT API access**.  
> You can mix **Win32, ATL, WTL, COM, DirectX, and C++17 features** freely.  
> Only UWP / AppContainer introduces restrictions


## 3️⃣ Key Points

1. **C++/WinRT is header-only**
    - `winrt::init_apartment()` initializes the COM/WinRT runtime.
    - You can call any **WinRT API** like `AnalyticsInfo::VersionInfo()` here.
        
2. **Win32 APIs coexist**
    
    - You can still create a classic window (`CreateWindowExW`) and handle messages (`WndProc`).
        
3. **No sandbox**
    
    - This is a **fully native Win32 desktop app**, not UWP, so you have full OS access.
        
4. **C++17 Features**
    
    - Use structured bindings, `std::filesystem`, `std::optional`, etc., freely alongside C++/WinRT.


```cpp


/*Some WinRT APIs require linking against `WindowsApp.lib`.

**Project → Properties → Linker → Input → Additional Dependencies**  
Add:

`WindowsApp.lib`*/

#include <atlbase.h>
#include <atlapp.h>
#include <atlwin.h>
#include <atlframe.h>
#include <atlctrls.h>
#include <atlstr.h>

#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.System.Profile.h>

CAppModule _Module;

//-------------------------------------------
// Main WTL Frame Window
class CMainWindow : public CFrameWindowImpl<CMainWindow>
{
public:
    DECLARE_FRAME_WND_CLASS(L"WTLWinRTExampleWindow", 0)

    BEGIN_MSG_MAP(CMainWindow)
        MESSAGE_HANDLER(WM_CREATE, OnCreate)
        MESSAGE_HANDLER(WM_PAINT, OnPaint)
        MESSAGE_HANDLER(WM_DESTROY, OnDestroy)
        CHAIN_MSG_MAP(CFrameWindowImpl<CMainWindow>)
    END_MSG_MAP()

    LRESULT OnCreate(UINT, WPARAM, LPARAM, BOOL&)
    {
        CenterWindow();
        return 0;
    }

    LRESULT OnPaint(UINT, WPARAM, LPARAM, BOOL&)
    {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(&ps);
        RECT rc;
        GetClientRect(&rc);

        // Classic Win32/WTL drawing
        DrawTextW(hdc, L"Hello WTL + C++/WinRT!", -1, &rc,
            DT_CENTER | DT_VCENTER | DT_SINGLELINE);

        // Example: C++/WinRT API call
        auto family = winrt::Windows::System::Profile::AnalyticsInfo::VersionInfo().ProductName();
       
        std::wstring familyStr = family.c_str();
        std::wstring info = std::wstring(L"\nDeviceFamily: ") + familyStr;
        DrawTextW(hdc, info.c_str(), -1, &rc, DT_CENTER | DT_TOP | DT_SINGLELINE);

        EndPaint(&ps);
        return 0;
    }

    LRESULT OnDestroy(UINT, WPARAM, LPARAM, BOOL&)
    {
        PostQuitMessage(0);
        return 0;
    }
};

//-------------------------------------------
int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE, PWSTR, int nCmdShow)
{
    // Initialize WTL
    _Module.Init(nullptr, hInstance);

    // Initialize C++/WinRT
    winrt::init_apartment();

    CMainWindow wndMain;
    if (wndMain.CreateEx() == NULL)
        return 0;

    wndMain.ShowWindow(nCmdShow);
    wndMain.UpdateWindow();

    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0) > 0)
    {
       
            TranslateMessage(&msg);
            DispatchMessage(&msg);
       
    }

    winrt::uninit_apartment();
    _Module.Term();
    return 0;
}

```