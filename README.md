# Blender Addon: Low-High-Poly-Name-Setter
Helper for simplified LP/HP naming before export or baking.
## Description
If you've ever had to manually assign names and suffixes for Low-Poly and High-Poly objects, you know how tedious it can be. Forget about the routine—this addon takes care of it for you.  

Originally developed for personal use, it has been crafted with care to be as convenient and efficient for others as it is for me.

## How to Use

- **Quick Collection Assignment:** Select your model and click "Low-Poly" or "High-Poly." The model will be moved into the corresponding collection, which will be created automatically if it doesn't exist.  
- **Set Names:** Select similar parts in Low-Poly and High-Poly and click "Set Names." Models are hidden automatically to avoid clutter (this can be disabled in settings).  
- **Automatic Indexing:** Indices increment automatically by 1 (optional in settings). Continue "hiding" the model as you go.  
- **Attach Extra Parts:** If any leftover parts remain, select the part and the target it belongs to, then click "Attach." Names are applied automatically.  
- **Export:** Export both collections to a specified folder with one click. Re-clicking will overwrite existing files. Use Low-Poly and High-Poly checkboxes to avoid exporting unnecessary collections.  
- **Multiple Objects:** Add objects in the "Set Collection" tab and work with multiple objects at once. Switch between them—export and other operations affect only the active object.  
- **Combined Export:** You can also export all Low-Poly objects from collections into a single FBX using "Export Combined LowPoly."

## Installation

1. Go to the **Releases** section of this repository.  
2. Download the addon **.zip** file (do not unpack it).  
3. Install it in Blender in one of two ways:
   - **Edit → Preferences → Add-ons → Install…**, then select the downloaded `.zip`;
   - **or simply drag and drop the `.zip` file into the Blender window**.

## Example
![Addon Panel](images/panel.png)

## Video
Embed a video using YouTube or link to a local file. Example for YouTube:  

```markdown
[![Video Title](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
