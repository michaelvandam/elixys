package Elixys.Subviews
{
	import Elixys.Assets.*;
	import Elixys.Components.Screen;
	import Elixys.Extended.Form;
	import Elixys.Extended.Input;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.State.Reagent;
	import Elixys.JSON.State.Sequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObjectContainer;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.getQualifiedClassName;

	// This subview baset is an extension of our extended Form class
	public class SubviewBase extends Form
	{
		/***
		 * Construction
		 **/
		
		public function SubviewBase(screen:Sprite, sMode:String, pElixys:Elixys, sSubviewType:String, 
									nButtonWidth:Number, pViewXML:XML, pEditXML:XML, pRunXML:XML,
									attributes:Attributes)
		{
			// Remember the mode, elixys and subview type
			m_sMode = sMode;
			m_pElixys = pElixys;
			m_sSubviewType = sSubviewType;

			// Call the base constructor
			var pXML:XML;
			switch (m_sMode)
			{
				case Constants.VIEW:
					pXML = pViewXML;
					break;
				
				case Constants.EDIT:
					pXML = pEditXML;
					break;
				
				case Constants.RUN:
					pXML = pRunXML;
					break;
			}
			super(screen, pXML, attributes);
			
			// Start invisible
			visible = false;
		}

		/***
		 * Member functions
		 **/

		// Updates the sequence
		public function UpdateSequence(pSequence:Sequence):void
		{
			m_pSequence = pSequence;
		}

		// Updates the component
		public function UpdateComponent(pComponent:ComponentBase):void
		{
		}
		
		// Returns the subview type
		public function get SubviewType():String
		{
			return m_sSubviewType;
		}

		// Adds a skin
		protected function AddSkin(pClass:Class):MovieClip
		{
			return AddSkinAt(pClass, numChildren);
		}

		// Adds a skin at the specified index
		protected function AddSkinAt(pClass:Class, nIndex:int):MovieClip
		{
			var pSkin:MovieClip = new pClass() as MovieClip;
			pSkin.buttonMode = false;
			addChildAt(pSkin, nIndex);
			return pSkin;
		}

		// Adds a skin and scales to a given width
		protected function AddSkinWidth(pClass:Class, nWidth:Number):MovieClip
		{
			var pSkin:MovieClip = AddSkin(pClass);
			pSkin.width = m_nButtonWidth;
			pSkin.scaleY = pSkin.scaleX;
			return pSkin;
		}

		// Adds a label
		protected function AddLabel(sFontFace:String, nFontSize:int, sAlign:String):UILabel
		{
			var pXML:XML =
				<label useEmbedded="true" alignH="left" alignV="bottom">
					<font face={sFontFace} size={nFontSize} />
				</label>;
			var pLabel:UILabel = CreateLabel(pXML, attributes);
			var pTextFormat:TextFormat = pLabel.getTextFormat();
			pTextFormat.align = sAlign;
			pLabel.setTextFormat(pTextFormat);
			return pLabel;
		}

		// Adds an input
		protected function AddInput(nFontSize:int, sFontColor:String, sReturnKeyLabel:String):Input
		{
			var pXML:XML =
				<input size={nFontSize} alignH="fill" color={sFontColor} 
					skin={getQualifiedClassName(TextInput_upSkin)} 
					returnKeyLabel={sReturnKeyLabel} />;
			return CreateInput(pXML, attributes);
		}
		
		// Post the component to the server
		protected function PostComponent(pComponent:ComponentBase):void
		{
			// Locate the screen
			var pParent:DisplayObjectContainer = this;
			while (pParent != null)
			{
				if (pParent is Screen)
				{
					(pParent as Screen).DoPost(pComponent, "sequence/" + m_pSequence.Metadata.ID + "/component/" + 
						pComponent.ID);
					return;
				}
				pParent = pParent.parent;
			}
		}

		// Post the reagent to the server
		protected function PostReagent(pReagent:Reagent):void
		{
			// Locate the screen
			var pParent:DisplayObjectContainer = this;
			while (pParent != null)
			{
				if (pParent is Screen)
				{
					(pParent as Screen).DoPost(pReagent, "sequence/" + m_pSequence.Metadata.ID + "/reagent/" + 
						pReagent.ReagentID);
					return;
				}
				pParent = pParent.parent;
			}
		}
		
		/***
		 * Member variables
		 **/

		// Input parameters
		protected var m_sMode:String;
		protected var m_pElixys:Elixys;
		protected var m_sSubviewType:String;
		protected var m_nButtonWidth:Number;
		
		// Current sequence
		protected var m_pSequence:Sequence;
		
		// Keyboard focus region for panning
		protected var m_nInputAreaOfInterestTop:uint;
		protected var m_nInputAreaOfInterestBottom:uint;
	}
}
