package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Events.SelectionEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.State.Sequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.utils.*;
	
	// This sequence tools component is an extension of our extended Form class
	public class SequenceTools extends Form
	{
		/***
		 * Construction
		 **/
		
		public function SequenceTools(screen:Sprite, xml:XML, attributes:Attributes, nUnitOperationWidth:Number,
									  nButtonSkinWidth:Number)
		{
			// Call the base constructor
			super(screen, SEQUENCETOOLS, attributes);
		}
		
		/***
		 * Member functions
		 **/

		/***
		 * Member variables
		 **/
		
		// Sequence tools XML
		protected static const SEQUENCETOOLS:XML = 
			<frame background="#FF00FF" />;
	}
}
