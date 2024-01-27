# pyseq - docs

## Basic concepts
The three main concepts are:
- the realm, which is the overarching environment where everything else happens
- the vault, which is the mechanism to ensure persistence, and that provides the realm information about which imps to instantiate
- the imps, which represent any other component that is acting in the realm, again using the vault for data persistence across reload of the application or reload of modules

### realm
- the realm module is configured with a dictionary of "imps", which are defined by a module and a class
- realm will cyclically verify that instances of the right imps are in the imps dictionary, if not it either creates or kills them
- imps start frozen, not active. realm will try to unfreeze them every X seconds
- realm allows for respawning of imps, which means freezing all the imps from the modules from where the imps to be respawned come from, reloading the modules, and replacing the imps with new ones, which are then unfrozen

### vault
- the vault module stores configuration data for python modules and imp instances in a json file
- vault also manages reloads of modules
- modules just import vault and then register (or enchant), which stores the callback functions to get/set persistence data, and to handle reload behaviours
- modules registered in the vault receive a callback on_after_load(token2) every time they are (re)loaded. token2 is None the first time, and then it's whatever is returned by on_before_load() (if any) for subsequent times
- vault provides a get_my_data and set_my_data functions to retrieve or update the contents of the vault on request of the module
- callbacks have a default name/behaviour if not specified
  - on_before_load(token1) -> toke2:Any is called before reload
  - on_after_load(token2, token1) -> None is called after (re)load
  - get_vault_data(token1) -> data:Any is called whenever vault needs to serialize the data
  - set_vault_data(token1, data) -> None is called whenever data are deserialized and need to be loaded in the module. this will be done  after the first on_after_load if the module is loaded when vault has already deserialised data for it
  - if a module has no get/set vault data but has an object called vault_data, vault will just get/set that one as required. note that setting will NOT replace the object but only its contents expecting it to be either a dictionary or an AttrDict
- modules are responsible to maintain consistent states within reloads using whatever means (callbacks or whatever). a simple method to do so is:
  - X = globals().get("X", default initial value)
  - this will preserve the contents of X across reloads, initialising it only once

## Imps
### enchanter
- this is maybe specific to the pyseq implementation
- the enchanter is an imp itself, to allow for respawning during development/debug
- the various imps will interact with the outside world (midi controllers, synths and so on) following the instructions of the enchanter, who is responsible to configure and orchestrate them
- some imps will also report to the enchanter events from the outside, for instance interactions with the user asking to change configuration parameters
- this ensures that all runtime configuration is managed consistently for all the imps, and that the logic to implement user interfaces and interact with external controllers (both for input and output) is separate from the logic to configure

### bard
- the bard is an imp itself, to allow for respawning during development/debug
- the bard is the one who directs the notes to be played based on the inputs from the imps listening to midi input interfaces and all kind of configuration it has stored (velocity filters, note reassignment for scales, note expansion for chords, patter generation for arpeggios or sequencing, e.g. in a drum machine mode, and global transpose)
- the bard is configured by the enchanter, and sends commands to numbered imps that then pass them to the actual output instruments

### others
Other imps are:
- controllers, which define the specific logic to deal with specific midi controllers, in my case AKAI MPK mini mk3, Arturia MicroFreak, Yamaha P85, AKAI APC Keys 25
- synths, in my case only a wrapper for FluidSynth (for now)
- generic midi input/output for physical or virtual ports. on windows virtual ports are not possible, the chosen workaround is to create them with loopMidi, and pyseq will just connect to one end of them