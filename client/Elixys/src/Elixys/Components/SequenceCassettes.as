package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Events.SelectionEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.SequenceComponent;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Rectangle;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.*;
	
	// This sequence cassettes component is an extension of our extended Form class
	public class SequenceCassettes extends Form
	{
		/***
		 * Construction
		 **/
		
		public function SequenceCassettes(screen:Sprite, xml:XML, attributes:Attributes, nUnitOperationWidth:Number,
										  nButtonSkinWidth:Number, pElixys:Elixys)
		{
			// Call the base constructor
			super(screen, SEQUENCECASSETTES, attributes);

			// Extract font details
			if (xml.@fontface.length() > 0)
			{
				m_sFontFace = xml.@fontface[0];
			}
			if (xml.@fontsize.length() > 0)
			{
				m_nFontSize = parseInt(xml.@fontsize[0]);
			}
			if (xml.@enabledtextcolor.length() > 0)
			{
				m_nEnabledTextColor = Styling.AS3Color(xml.@enabledtextcolor[0]);
			}
			if (xml.@activetextcolor.length() > 0)
			{
				m_nActiveTextColor = Styling.AS3Color(xml.@activetextcolor[0]);
			}
			if (xml.@pressedtextcolor.length() > 0)
			{
				m_nPressedTextColor = Styling.AS3Color(xml.@pressedtextcolor[0]);
			}

			// Remember the Elixys and button width
			m_pElixys = pElixys;
			m_nButtonWidth = nButtonSkinWidth;
			
			// Add event listeners
			addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
		}
		
		/***
		 * Member functions
		 **/

		// Called when the underlying component changes
		public function UpdateSelectedComponent(nComponentID:int):void
		{
			// Remember the component ID and render
			m_nComponentID = nComponentID;
			Render();
		}

		// Updates the sequence
		public function UpdateSequence(pSequence:Sequence):void
		{
			// Remember the sequence
			m_pSequence = pSequence;
			
			// Adjust the number of cassette skins, labels and hit areas
			m_nCassettes = m_pElixys.GetConfiguration().Reactors;
			while (m_pUpSkins.length < m_nCassettes)
			{
				m_pUpSkins.push(AddSkin(tools_btn_up));
				m_pDownSkins.push(AddSkin(tools_btn_down));
				m_pActiveSkins.push(AddSkin(tools_btn_active));
				m_pLabels.push(AddLabel());
				m_pHitAreas.push(new Rectangle());
				
			}
			while (m_pUpSkins.length > m_nCassettes)
			{
				removeChild(m_pUpSkins.pop());
				removeChild(m_pDownSkins.pop());
				removeChild(m_pActiveSkins.pop());
				removeChild(m_pLabels.pop());
				m_pHitAreas.pop();
			}
			
			// Render
			Render();
		}
		
		// Updates the component
		public function UpdateComponent(pComponent:ComponentBase):void
		{
			// Remember the component and render
			m_pComponent = pComponent;
			Render();
		}

		// Render the component
		protected function Render():void
		{
			if (m_pSequence != null)
			{
				// Update the buttons and labels
				m_nSelectedIndex = -1;
				var nIndex:int, pComponent:SequenceComponent, pLabel:UILabel, pHitArea:Rectangle;
				var pUpSkin:MovieClip, pDownSkin:MovieClip, pActiveSkin:MovieClip;
				var nOffsetX:Number = (attributes.width - (m_nButtonWidth * m_nCassettes) -
					(BUTTON_HORIZONTAL_GAP * (m_nCassettes - 1))) / 2;
				for (nIndex = 0; nIndex < m_nCassettes; ++nIndex)
				{
					// Set the skin visibility
					pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
					pUpSkin = m_pUpSkins[nIndex] as MovieClip;
					pDownSkin = m_pDownSkins[nIndex] as MovieClip;
					pActiveSkin = m_pActiveSkins[nIndex] as MovieClip;
					if (pComponent.ID == m_nComponentID)
					{
						m_nSelectedIndex = nIndex;
					}
					ReleaseButton(nIndex);
					
					// Set the skin size and position
					pUpSkin.width = pDownSkin.width = pActiveSkin.width = m_nButtonWidth;
					pUpSkin.scaleY = pDownSkin.scaleY = pActiveSkin.scaleY = pUpSkin.scaleX;
					pUpSkin.x = pDownSkin.x = pActiveSkin.x = nOffsetX;
					pUpSkin.y = pDownSkin.y = pActiveSkin.y = BUTTON_VERTICAL_GAP;
					
					// Set the label text and position
					pLabel = m_pLabels[nIndex] as UILabel;
					pLabel.width = pUpSkin.width;
					pLabel.text = (nIndex + 1).toString();
					pLabel.width = pLabel.textWidth + 5;
					pLabel.x = pUpSkin.x + ((pUpSkin.width - pLabel.width) / 2);
					pLabel.y = pUpSkin.y + ((pUpSkin.height - pLabel.height) / 2);
					
					// Update the hit area
					pHitArea = m_pHitAreas[nIndex] as Rectangle;
					pHitArea.x = pUpSkin.x;
					pHitArea.y = pUpSkin.y;
					pHitArea.width = pUpSkin.width;
					pHitArea.height = pUpSkin.height;

					// Update the offset
					nOffsetX += m_nButtonWidth + BUTTON_HORIZONTAL_GAP;
				}
			}
			
			// Update the quick view text
		}

		// Adds a skin
		protected function AddSkin(pClass:Class):MovieClip
		{
			var pSkin:MovieClip = new pClass() as MovieClip;
			pSkin.buttonMode = false;
			addChild(pSkin);
			return pSkin;
		}

		// Adds a label
		protected function AddLabel():UILabel
		{
			var pXML:XML =
				<label useEmbedded="true" alignH="left" alignV="bottom">
					<font face={m_sFontFace} size={m_nFontSize} />
				</label>;
			var pLabel:UILabel = CreateLabel(pXML, attributes);
			var pTextFormat:TextFormat = pLabel.getTextFormat();
			pTextFormat.align = TextFormatAlign.CENTER;
			pLabel.setTextFormat(pTextFormat);
			return pLabel;
		}
		
		// Called when the user presses the mouse button
		protected function OnMouseDown(event:MouseEvent):void
		{
			// Check for button clicks
			for (var nIndex:int = 0; nIndex < m_nCassettes; ++nIndex)
			{
				if ((m_pHitAreas[nIndex] as Rectangle).contains(mouseX, mouseY))
				{
					// Press the button and wait for mouse up
					m_nPressedIndex = nIndex;
					PressButton(m_nPressedIndex);
					stage.addEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
					break;
				}
			}
		}
		
		// Called when the user releases the mouse button
		protected function OnMouseUp(event:MouseEvent):void
		{
			// Remove the event listener and release the button
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
			ReleaseButton(m_nPressedIndex);
			
			// Check if the mouse was release over the same button that was initially clicked
			if ((m_pHitAreas[m_nPressedIndex] as Rectangle).contains(mouseX, mouseY))
			{
				// Dispatch a selection change event
				var pComponent:SequenceComponent = m_pSequence.Components[m_nPressedIndex] as SequenceComponent;
				dispatchEvent(new SelectionEvent(pComponent.ID));
			}
			m_nPressedIndex = -1;
		}
		
		// Draws the button in the pressed state
		protected function PressButton(nIndex:int):void
		{
			(m_pUpSkins[nIndex] as MovieClip).visible = false;
			(m_pDownSkins[nIndex] as MovieClip).visible = true;
			(m_pActiveSkins[nIndex] as MovieClip).visible = false;
			(m_pLabels[nIndex] as UILabel).textColor = m_nPressedTextColor;
		}
		
		// Draws the button in the released state
		protected function ReleaseButton(nIndex:int):void
		{
			(m_pUpSkins[nIndex] as MovieClip).visible = (nIndex != m_nSelectedIndex);
			(m_pDownSkins[nIndex] as MovieClip).visible = false;
			(m_pActiveSkins[nIndex] as MovieClip).visible = (nIndex == m_nSelectedIndex);
			if (nIndex == m_nSelectedIndex)
			{
				(m_pLabels[nIndex] as UILabel).textColor = m_nActiveTextColor;
			}
			else
			{
				(m_pLabels[nIndex] as UILabel).textColor = m_nEnabledTextColor;
			}
		}
		
		/***
		 * Member variables
		 **/
		
		// Sequence cassette XML
		protected static const SEQUENCECASSETTES:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} />;

		// Elixys reference
		protected var m_pElixys:Elixys;
		
		// Number of cassettes
		protected var m_nCassettes:int;

		// Button width
		protected var m_nButtonWidth:Number;
		
		// Font details
		protected var m_sFontFace:String = "";
		protected var m_nFontSize:int = 0;
		protected var m_nEnabledTextColor:uint = 0;
		protected var m_nActiveTextColor:uint = 0;
		protected var m_nPressedTextColor:uint = 0;

		// Skin, label and hit test arrays
		protected var m_pUpSkins:Array = new Array();
		protected var m_pDownSkins:Array = new Array();
		protected var m_pActiveSkins:Array = new Array();
		protected var m_pLabels:Array = new Array();
		protected var m_pHitAreas:Array = new Array();

		// Current state
		protected var m_nComponentID:int = -1;
		protected var m_pSequence:Sequence;
		protected var m_pComponent:ComponentBase;

		// Selected and pressed indicies
		protected var m_nSelectedIndex:int = -1;
		protected var m_nPressedIndex:int = -1;
		
		// Constants
		protected static var BUTTON_HORIZONTAL_GAP:int = 10;
		protected static var BUTTON_VERTICAL_GAP:int = 20;
	}
}
