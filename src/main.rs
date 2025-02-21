//! This example is used to test how transforms interact with alpha modes for [`Mesh2d`] entities with a [`MeshMaterial2d`].
//! This makes sure the depth buffer is correctly being used for opaque and transparent 2d meshes

use bevy::{
    color::palettes::css::{BLUE, GREEN, WHITE},
    prelude::*,
    sprite::AlphaMode2d,
    render::camera::ScalingMode,
    window::Window,
};

use bevy::{color::palettes::tailwind::*, picking::pointer::PointerInteraction, prelude::*};

// struct for hero with json data, with component
#[derive(Component)]
struct Hero {
    data: serde_json::Value,
    selected: bool,
}

fn main() {
    App::new()
    .add_plugins((DefaultPlugins, MeshPickingPlugin))
    .add_systems(Startup, setup)
    .run();
}

fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    commands.spawn((Camera2d,
        Transform::from_xyz(0.0, 0.0, 0.0),
        Projection::Orthographic(OrthographicProjection {
            scaling_mode: ScalingMode::FixedVertical { viewport_height: 5000.0 },
            ..OrthographicProjection::default_2d()
        })
    ));

    let white_matl = materials.add(Color::WHITE);
    let ground_matl = materials.add(Color::from(GRAY_300));
    let hover_matl = materials.add(Color::from(CYAN_300).with_alpha(0.5));
    let pressed_matl = materials.add(Color::from(YELLOW_300));


    let files: Vec<_> = std::fs::read_dir("assets/mm_images").unwrap().collect::<Result<_, _>>().unwrap();

    // create vector of texture handles
    let mut texture_handles:Vec<Handle<Image>> = Vec::new();

    // read json file
    let json_string = std::fs::read_to_string("assets/data/processed/heroes.json").unwrap();
    let heroes: serde_json::Value = serde_json::from_str(&json_string).unwrap();
    
    // list heroes
    for key in heroes.as_object().unwrap().keys() {
        // println!("key: {}", key);
        // print hero name
        let name = heroes[key]["name"].as_str().unwrap();
        // print the name excluding the first 5 characters
        // println!("name: {}", &name[5..]);
        

        let mut img_found = false;
        for file in &files {
            let path = file.path();
            let file_name = path.file_name().unwrap().to_str().unwrap().to_string();
            // println!("file_name: {}", file_name);
            // if file_name contains key
            if !file_name.contains(&name[5..]) {
                continue;
            }
            img_found = true;
            let texture_handle:Handle<Image> = asset_server.load(format!("mm_images/{}", file_name));
            texture_handles.push(texture_handle);
        }
        if !img_found {
            println!("image not found for hero: {}", key);
        }
    }



    // list file in mm_images folder


    let mesh_handle = meshes.add(Rectangle::from_size(Vec2::splat(256.0)));



    for i in 0..texture_handles.len() {
        let texture_handle = texture_handles[i].clone();
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

        let x = i as f32 * 256.0 - 3000.0;
        let y = 2000.0;
        let z = 1.0;

        commands.spawn((
            Mesh2d(mesh_handle.clone()),
            MeshMaterial2d(material.clone()),
            Transform::from_xyz(x, y, z),
            Hero {
                data: heroes[i].clone(),
                selected: false,
            },
        ))
        .observe(update_material_on::<Pointer<Over>>(hover_mat.clone()))
        .observe(update_material_on::<Pointer<Out>>(material.clone()))
        .observe(update_material_on::<Pointer<Up>>(hover_mat.clone()))
        .observe(select_hero::<Pointer<Down>>(selected_mat.clone()));

    }
}


// // this system check if the user clicked on any of the meshes
// fn mouse_input_system(
//     mut commands: Commands,
//     buttons: Res<ButtonInput<MouseButton>>,
//     mut query: Query<(Entity, &Transform, &Mesh2d)>,
// ) {
//     if buttons.just_pressed(MouseButton::Left) {
//         let window = windows.get_primary().unwrap();
//         let cursor_position = window.cursor_position().unwrap();
//         let cursor_position = Vec2::new(cursor_position.x as f32, cursor_position.y as f32);

//         for (entity, transform, mesh) in query.iter() {
//             let mesh = mesh.0.clone();
//             let mesh = mesh.read().unwrap();
//             let mesh = mesh.as_ref().unwrap();
//             let mesh = mesh.downcast_ref::<Rectangle>().unwrap();

//             let size = mesh.size;
//             let half_size = size / 2.0;
//             let min = transform.translation - half_size.extend(0.0);
//             let max = transform.translation + half_size.extend(0.0);

//             if cursor_position.x >= min.x
//                 && cursor_position.x <= max.x
//                 && cursor_position.y >= min.y
//                 && cursor_position.y <= max.y
//             {
//                 commands.entity(entity).despawn();
//             }
//         }
//     }
// }

/// Returns an observer that updates the entity's material to the one specified.
fn update_material_on<E>(
    new_material: Handle<ColorMaterial>,
) -> impl Fn(Trigger<E>, Query<(&mut MeshMaterial2d<ColorMaterial>, &mut Hero)>) {
    // An observer closure that captures `new_material`. We do this to avoid needing to write four
    // versions of this observer, each triggered by a different event and with a different hardcoded
    // material. Instead, the event type is a generic, and the material is passed in.
    move |trigger, mut query| {
        if let Ok((mut material, mut hero)) = query.get_mut(trigger.entity()) {
            if !hero.selected {
                material.0 = new_material.clone();
            }

        }
    }
}

fn select_hero<E>(
    new_material: Handle<ColorMaterial>,
) -> impl Fn(Trigger<E>, Query<(&mut MeshMaterial2d<ColorMaterial>, &mut Hero)>) {
    // An observer closure that captures `new_material`. We do this to avoid needing to write four
    // versions of this observer, each triggered by a different event and with a different hardcoded
    // material. Instead, the event type is a generic, and the material is passed in.
    move |trigger, mut query| {
        if let Ok((mut material, mut hero)) = query.get_mut(trigger.entity()) {
            hero.selected = !hero.selected;
            if hero.selected {
                material.0 = new_material.clone();
            }
        }
    }
}
