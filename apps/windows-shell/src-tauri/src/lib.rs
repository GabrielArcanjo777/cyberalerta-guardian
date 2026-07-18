// Casca nativa Windows (Plano Mestre v1.1, Secao 3.4/8.6). Nao hospeda
// FastAPI/backend local — so autentica e consome o nucleo cloud, igual ao
// Web. Tray + deep links + updater sao a unica logica nativa real; todo o
// resto (Console/Admin/MFA) e o mesmo frontend estatico da Web, servido a
// partir de frontendDist.
use tauri::{
    menu::{Menu, MenuItem},
    tray::TrayIconBuilder,
    Emitter, Manager,
};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_deep_link::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .setup(|app| {
            let status_item =
                MenuItem::with_id(app, "status", "Protecao ativa", false, None::<&str>)?;
            let console_item =
                MenuItem::with_id(app, "console", "Abrir Console", true, None::<&str>)?;
            let disconnect_item =
                MenuItem::with_id(app, "disconnect", "Desconectar", true, None::<&str>)?;
            let quit_item = MenuItem::with_id(app, "quit", "Sair", true, None::<&str>)?;
            let menu = Menu::with_items(
                app,
                &[&status_item, &console_item, &disconnect_item, &quit_item],
            )?;

            TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .show_menu_on_left_click(true)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => app.exit(0),
                    "console" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    "disconnect" => {
                        // A logica real de logout (chamar /auth/logout e limpar o
                        // cookie jar do plugin HTTP) fica no frontend, que já a
                        // implementa pro Web — o tray so emite o evento e mostra
                        // a janela pra o usuario ver o resultado.
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.emit("tray://disconnect-requested", ());
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    _ => {}
                })
                .build(app)?;

            Ok(())
        })
        // Fechar a janela minimiza pra tray em vez de encerrar o processo —
        // "o backend continua operando com o aplicativo fechado" (aceite da
        // Sprint 4) significa que fechar a janela nao deve nem precisar
        // encerrar o app local, mas minimizar pra tray e o comportamento mais
        // familiar pro publico-alvo (Seção 3.4: tray com status/abrir/sair).
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                let _ = window.hide();
                api.prevent_close();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
