//! This example is used to test how transforms interact with alpha modes for [`Mesh2d`] entities with a [`MeshMaterial2d`].
//! This makes sure the depth buffer is correctly being used for opaque and transparent 2d meshes

use bevy::{
    color::palettes::css::{BLUE, RED, WHITE}, 
    input::mouse::MouseWheel, 
    prelude::*, 
    reflect::TypePath,
    sprite::AlphaMode2d, 
    window::Window,
    render::view::visibility::RenderLayers,
    window::PrimaryWindow,
    app::AppExit,
    input::mouse::MouseScrollUnit
};

use std::collections::HashMap;
use bevy_common_assets::json::JsonAssetPlugin;
use serde;




#[derive(serde::Deserialize, bevy::asset::Asset, bevy::reflect::TypePath, Debug, Clone)]
struct HeroData{
    abilities: Vec<String>,
    name: String,
    iname: String,
    level_up_upgrades: HashMap<String, f32>,
    starting_stats: HashMap<String, f32>,
    weapon: HashMap<String, f32>,
    weapon_name: String,
    image_location: String,
}

#[derive(serde::Deserialize, Asset, TypePath)]
struct HeroDatas {
    heroes: Vec<HeroData>,
}

#[derive(Resource)]
struct HeroDataHandle(Handle<HeroDatas>);


#[derive(serde::Deserialize, bevy::asset::Asset, bevy::reflect::TypePath, Debug, Clone)]
struct level_data{
    m_unRequiredGold: i32,
    m_mapBonusCurrencies: Option<HashMap<String, i32>>,
    m_bUseStandardUpgrade: Option<bool>,
}

#[derive(serde::Deserialize, Asset, TypePath)]
struct LevelDatas {
    levels: HashMap<i32, level_data>,
}

#[derive(Resource)]
struct LevelDataHandle(Handle<LevelDatas>);


#[derive(Debug, Clone, Copy, Default, Eq, PartialEq, Hash, States)]
enum AppState {
    #[default]
    Loading,
    Level,
    UpdateHeroes,
    DrawData,
    ClearCamera,
}
// struct for hero with json data, with component
#[derive(Component)]
struct Hero {
    selected: bool,
    highlighted: bool,
    n_souls: i32,
    hd: HeroData,
    dps: Option<Vec<f32>>,
}

#[derive(Component)]
struct HeroSelectCamera;


fn calc_dps(hero: &Hero, level_datas: &LevelDatas) -> Vec<f32> {
    // create a vector of f32 to store the dps per level
    let mut dps_per_level: Vec<f32> = Vec::new();
    let mut level: i32 = 0;
    let mut n_boons: i32 = 0;
    let mut s: i32 = 0;
    let damage_duration = 10_000;
    // loop through the souls
    while s <= hero.n_souls {
        // check if the souls is equal to the next level
        if s == level_datas.levels[&(level+1)].m_unRequiredGold as i32 {
            level += 1;
            let boon = level_datas.levels[&level].m_bUseStandardUpgrade;
            if boon.is_some() {
                n_boons += 1;
            }
        }

        let mut b_damage = hero.hd.weapon["Bullet Damage"];

        b_damage += n_boons as f32 * hero.hd.level_up_upgrades["MODIFIER_VALUE_BASE_BULLET_DAMAGE_FROM_LEVEL"];
        let shot_damage = b_damage * hero.hd.weapon["Bullets"];
        let dpm = shot_damage * hero.hd.weapon["ClipSize"];
        let time_to_reloaded_clip = hero.hd.weapon["CycleTime"] * hero.hd.weapon["ClipSize"] + hero.hd.weapon["ReloadDuration"];
        let mags_to_fire = (damage_duration as f32 / time_to_reloaded_clip) as i32;
        let damage = mags_to_fire as f32 * dpm;
        let dps = damage / damage_duration as f32;
        dps_per_level.push(dps);

        s += 1;
    }

    return dps_per_level;

    
}

fn main() {
    App::new()
    .add_plugins((DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                // provide the ID selector string here
                canvas: Some("#mygame-canvas".into()),
                // ... any other window properties ...
                ..default()
            }),
            ..default()
        }), 
        MeshPickingPlugin,
        JsonAssetPlugin::<HeroDatas>::new(&["hero.json"]),
        JsonAssetPlugin::<LevelDatas>::new(&["level.json"]),
    ))
    .init_state::<AppState>()
    .add_systems(Startup, setup)
    .add_systems(Update, spawn_level.run_if(in_state(AppState::Loading)))
    .add_systems(Update, update_heroes.run_if(in_state(AppState::UpdateHeroes)))
    .add_systems(Update, draw_data.run_if(in_state(AppState::DrawData)))
    .add_systems(Update, clear_camera.run_if(in_state(AppState::ClearCamera)))
    .add_systems(Update, zoom_camera)
    .add_systems(Update, keyboard_control)
    .run();
}

fn update_heroes(
    mut commands: Commands,
    mut state: ResMut<NextState<AppState>>,
    mut h_q: Query<(&mut MeshMaterial2d<ColorMaterial>, &mut Hero)>,
    levels: Res<LevelDataHandle>,
    levelss: Res<Assets<LevelDatas>>,
) {
    let levels = levelss.get(levels.0.id()).unwrap();

    let mut min_dps = 100.0;
    for (_, mut hero) in &mut h_q {

        if hero.selected {
            hero.dps = Some(calc_dps(&hero, &levels));
            if hero.dps.as_ref().unwrap()[0] < min_dps {
                min_dps = hero.dps.as_ref().unwrap()[0];
            }
        }
    }
    println!("min dps: {:?}", min_dps);
    state.set(AppState::DrawData);
}

fn clear_camera(
    mut state: ResMut<NextState<AppState>>,
    mut query: Query<(&mut Camera), (With<Camera2d>, Without<HeroSelectCamera>)>,
)
{
    // let mut camera = query.single_mut();
    // camera.clear_color = ClearColorConfig::None;

    state.set(AppState::Level);

}

fn draw_data(
    mut commands: Commands,
    mut state: ResMut<NextState<AppState>>,
    mut h_q: Query<(&mut MeshMaterial2d<ColorMaterial>, &mut Hero)>,
    mut gizmos: Gizmos,
    time: Res<Time>,
) {
    // clear camera ?
    let height = 640.;
    let width= 1200.;
    gizmos.line_2d(Vec2::new(0.0, 0.0), Vec2::new(width, 0.0), BLUE);
    gizmos.line_2d(Vec2::new(0.0, 0.0), Vec2::new(0.0, height), RED);

    for (_, mut hero) in &mut h_q {

        if hero.selected {
            let xscale = 0.01;
            let yscale = 10.0;
            let y_start = 10.0;
            let mut i = 0;
            let mut last_dps = 0.0;
            for dps in hero.dps.as_ref().unwrap() {
                if last_dps == 0.0 {
                    last_dps = *dps;
                    i += 1;
                    continue;
                }
                let x1 = (i - 1) as f32 * xscale;
                let y1 = (last_dps - y_start) * yscale;
                let x2 = i as f32 * xscale;
                let y2 = (dps - y_start) * yscale;

                if hero.highlighted {
                    gizmos.line_2d(Vec2::new(x1, y1), Vec2::new(x2, y2), WHITE);
                } else {
                    gizmos.line_2d(Vec2::new(x1, y1), Vec2::new(x2, y2), WHITE.with_alpha(0.5));
                }
                // gizmos.line_2d(Vec2::new(x1, y1), Vec2::new(x2, y2), WHITE);
                last_dps = *dps;


                i += 1;
            }
        }
    }
    // state.set(AppState::ClearCamera);
}


fn spawn_level(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    heroes: Res<HeroDataHandle>,
    mut heroess: ResMut<Assets<HeroDatas>>,
    mut state: ResMut<NextState<AppState>>,
    asset_server: Res<AssetServer>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    if let Some(heroes) = heroess.remove(heroes.0.id()) {

        let mesh_handle = meshes.add(Rectangle::from_size(Vec2::splat(256.0)));
 
        let mut i: i32 = 0;
        let n_heores = heroes.heroes.len() as i32;
        for hero in &heroes.heroes {
            // println!("hero: {:?}", hero);

            let texture_handle:Handle<Image> = asset_server.load(hero.image_location.clone());
            let material = materials.add(ColorMaterial {
                color: WHITE.with_alpha(0.15).into(),
                alpha_mode: AlphaMode2d::Blend,
                texture: Some(texture_handle.clone()),
            });
    
            let hover_mat = materials.add(ColorMaterial {
                color: WHITE.with_alpha(0.5).into(),
                alpha_mode: AlphaMode2d::Blend,
                texture: Some(texture_handle.clone()),
            });
    
            let selected_mat = materials.add(ColorMaterial {
                color: WHITE.with_alpha(1.0).into(),
                alpha_mode: AlphaMode2d::Blend,
                texture: Some(texture_handle.clone()),
            });
    
            let width = n_heores as f32 * 256.0;
            let x = i as f32 * 256.0 - width / 2.0;
            let y = 2000.0;
            let z = 1.0;
    
            commands.spawn((
                Mesh2d(mesh_handle.clone()),
                MeshMaterial2d(material.clone()),
                Transform::from_xyz(x, y, z),
                Hero {
                    n_souls: 47000,
                    selected: false,
                    highlighted: false,
                    hd: hero.clone(),
                    dps: None,
                },
                RenderLayers::layer(1),
            ))
            .observe(hero_selector::<Pointer<Over>>(hover_mat.clone()))
            .observe(hero_selector::<Pointer<Out>>(material.clone()))
            .observe(hero_selector::<Pointer<Up>>(hover_mat.clone()))
            .observe(hero_selector::<Pointer<Down>>(selected_mat.clone()));

            i += 1;
            
        }

        state.set(AppState::Level);
    }
}

fn setup(mut commands: Commands, asset_server: Res<AssetServer>) {


    let hero_data = HeroDataHandle(asset_server.load("data/processed/heroes.json"));
    commands.insert_resource(hero_data);

    let level_data = LevelDataHandle(asset_server.load("data/processed/level_bonuses.json"));
    commands.insert_resource(level_data);

    commands.spawn((Camera2d,
        Transform::from_xyz(600.0, 320.0, 0.0),
        Projection::Orthographic(OrthographicProjection {
            // scaling_mode: ScalingMode::FixedVertical { viewport_height: 2500.0 },
            scale: 1.0,
            ..OrthographicProjection::default_2d()
        }),
        Camera {
            order: 1,
            clear_color: ClearColorConfig::None,
            ..Camera::default()
        },
        RenderLayers::from_layers(&[0])
    ));
    commands.spawn((Camera2d,
        Transform::from_xyz(0.0, 0.0, 0.0),
        Projection::Orthographic(OrthographicProjection {
            // scaling_mode: ScalingMode::FixedVertical { viewport_height: 2500.0 },
            scale: 7.0,
            ..OrthographicProjection::default_2d()
        }),
        Camera {
            order: 0,
            ..Camera::default()
        },
        RenderLayers::from_layers(&[1]),
        HeroSelectCamera
    ));
}

fn hero_selector<E>(
    new_material: Handle<ColorMaterial>,
) -> impl Fn(Trigger<E>, Query<(&mut MeshMaterial2d<ColorMaterial>, &mut Hero)>, ResMut<NextState<AppState>>) {
    // An observer closure that captures `new_material`. We do this to avoid needing to write four
    // versions of this observer, each triggered by a different event and with a different hardcoded
    // material. Instead, the event type is a generic, and the material is passed in.
    move |trigger, mut query, mut state| {
        let event = trigger.event_type().index();
        // println!("event: {:?}", event);
        if let Ok((mut material, mut hero)) = query.get_mut(trigger.entity()) {
            if event == 344 {
                hero.selected = !hero.selected;
            }
            if !hero.selected {
                if event == 340 { //hover
                    material.0 = new_material.clone();
                }
                else if event == 342 {
                    material.0 = new_material.clone();
                    hero.highlighted = false;
                }
            } else {
                if event == 344 {
                    state.set(AppState::UpdateHeroes);
                    material.0 = new_material.clone();
                }
                else if event == 340 { //hover
                    hero.highlighted = true;
                }
                else if event == 342 {
                    hero.highlighted = false;
                }
                
            }
            // println!("hero: {:?} highlighted {:?}", hero.hd.name, hero.highlighted);

        }
    }
}


fn zoom_camera(
    mut query: Query<(&mut OrthographicProjection, &mut Transform), (With<Camera2d>, Without<HeroSelectCamera>)>,
    mut evr_scroll: EventReader<MouseWheel>,
    q_windows: Query<&Window, With<PrimaryWindow>>,
) {
    
    for ev in evr_scroll.read() {
        let position = q_windows.single().cursor_position();
        if position.is_none() {
            return;
        }
        let position = position.unwrap();
        let h_height = q_windows.single().height() / 2.0;
        let h_width = q_windows.single().width() / 2.0;

        let zoom_speed = 15.0;
        // calculate distance from center of screen
        let distancex = ((position.x - h_width) / h_width).abs();
        let distancey = ((position.y - h_height) / h_height).abs();
        let (mut projection, mut transform) = query.single_mut();
        match ev.unit {
            MouseScrollUnit::Line => {
                // println!("position: {:?}", position);
                projection.scale -= ev.y / 100.0;
                if position.y > h_height {
                    transform.translation.y -= ev.y * zoom_speed * distancey;
                } else {
                    transform.translation.y += ev.y * zoom_speed * distancey;
                }
                if position.x > h_width {
                    transform.translation.x += ev.y * zoom_speed * distancex;
                } else {
                    transform.translation.x -= ev.y * zoom_speed * distancex;
                }
            }
            MouseScrollUnit::Pixel => {
                println!("Scroll (pixel units): vertical: {}, horizontal: {}", ev.y, ev.x);
            }
        }
    }
    
}

fn keyboard_control(
    keys: Res<ButtonInput<KeyCode>>,
    mut exit: EventWriter<AppExit>
) {
    if keys.pressed(KeyCode::KeyW) {
        if keys.pressed(KeyCode::ControlLeft){
            exit.send(AppExit::Success);
        }
    }
}