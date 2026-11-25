"""Use existing verified action bundler for five real mechanical studies."""
from bundle_einar_actions import bundle

if __name__=='__main__':
    bundle(sources_spec=[(f'security_{clip}01',f'robot_{clip}.glb') for clip in ['idle','walk','melee','hit','death']],
           output_folder='security_bundle01',output_name='robot_actions.glb',
           credits=[{'asset':'Security Bot Rig','author':'Blender Foundation','license':'CC BY4.0',
                     'url':'https://studio.blender.org/characters/security-bot/v1/',
                     'license_url':'https://creativecommons.org/licenses/by/4.0/'}],
           limitations=['Five authored mechanical studies; no final robot art acceptance',
                        'Forward Walk is nonloop, no gameplay root motion controller',
                        'Opaque visor approximation; sampled morph size unoptimized',
                        'Death flat-floor only; no inter-part collision/debris guarantee'])
