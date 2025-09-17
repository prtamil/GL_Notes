2. Key use-package keywords:

- `:ensure` - automatically installs the package if missing
- `:init` - code to run before loading
- `:config` - code to run after loading
- `:bind` - key bindings
- `:hook` - mode hooks
- `:after` - load after specific packages
```lsp

;; First, ensure use-package is installed
(unless (package-installed-p 'use-package)
  (package-refresh-contents)
  (package-install 'use-package))

(require 'use-package)

;; Basic usage - install and load a package
(use-package magit
  :ensure t  ; automatically install if not available
  :bind ("C-x g" . magit-status))

;; More complex example with :init and :config
(use-package company
  :ensure t
  :init
  (setq company-minimum-prefix-length 2
        company-idle-delay 0.2)
  :config
  (global-company-mode 1)
  :bind (:map company-active-map
              ("C-n" . company-select-next)
              ("C-p" . company-select-previous)))

;; Using :after to load after another package
(use-package company-box
  :ensure t
  :after company
  :hook (company-mode . company-box-mode))

;; Using :custom for customization
(use-package org
  :ensure t
  :custom
  (org-log-done 'time)
  (org-startup-indented t)
  :config
  (setq org-agenda-files '("~/org/")))

;; Using :commands for lazy loading
(use-package projectile
  :ensure t
  :commands (projectile-find-file projectile-switch-project)
  :bind-keymap ("C-c p" . projectile-command-map))

;; Example with :if conditional loading
(use-package eglot
  :ensure t
  :if (>= emacs-major-version 26)
  :hook ((python-mode . eglot-ensure)
         (rust-mode . eglot-ensure)))

;; Using :mode to associate with file extensions
(use-package markdown-mode
  :ensure t
  :mode ("\\.md\\'" . markdown-mode)
  :init
  (setq markdown-command "multimarkdown"))

```