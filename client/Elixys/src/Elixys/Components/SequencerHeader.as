package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentCassette;
	import Elixys.JSON.State.Column;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.SequenceComponent;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.*;
	
	// This sequencer header component is an extension of the Form class
	public class SequencerHeader extends Form
	{
		/***
		 * Construction
		 **/
		
		public function SequencerHeader(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, SEQUENCERHEADER, attributes);

			// Get references to view components
			m_pPreviousButton = Button(findViewById("previous"));
			m_pNextButton = Button(findViewById("next"));
			
			// Add event listeners
			m_pPreviousButton.addEventListener(ButtonEvent.CLICK, OnPreviousButton);
			m_pNextButton.addEventListener(ButtonEvent.CLICK, OnNextButton);
		}

		/***
		 * Member functions
		 **/
		
		// Update the sequence
		public function UpdateSequence(pSequence:Sequence):void
		{
			// Remember the sequence and update the buttons
			m_pSequence = pSequence;
			UpdateButtons();
		}
		
		// Update the selected component
		public function UpdateSelectedComponent(nComponentID:int):void
		{
			// Remember the selected component and update the buttons
			m_nSelectedComponentID = nComponentID;
			UpdateButtons();
		}
		
		// Updates the state of the buttons
		protected function UpdateButtons():void
		{
			// Determine the button states
			var bPreviousEnabled:Boolean = false;
			var bNextEnabled:Boolean = false;
			var pComponent:SequenceComponent;
			if ((m_pSequence != null) && (m_nSelectedComponentID != -1))
			{
				// Start with both button enabled
				bPreviousEnabled = true;
				bNextEnabled = true;
				
				// Locate the first non-cassette component
				for (var nIndex:int = 0; nIndex < m_pSequence.Components.length; ++nIndex)
				{
					pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
					if (pComponent.ComponentType != ComponentCassette.COMPONENTTYPE)
					{
						if (pComponent.ID == m_nSelectedComponentID)
						{
							// Disable the previous button
							bPreviousEnabled = false;
						}
						break;
					}
				}
				
				// Check the last unit operation
				pComponent = m_pSequence.Components[m_pSequence.Components.length - 1] as SequenceComponent;
				if (pComponent.ID == m_nSelectedComponentID)
				{
					// Disable the next button
					bNextEnabled = false;
				}				
			}
			else
			{
				bPreviousEnabled = false;
				bNextEnabled = false;
			}
			
			// Enable or disabled the buttons
			m_pPreviousButton.enabled = bPreviousEnabled;
			m_pNextButton.enabled = bNextEnabled;
		}
		
		// Called when the user clicks the previous button
		protected function OnPreviousButton(event:ButtonEvent):void
		{
			// Dispatch an event to advance to the previous unit operation
			dispatchEvent(new ButtonEvent("PREVIOUS"));
		}

		// Called when the user clicks the next button
		protected function OnNextButton(event:ButtonEvent):void
		{
			// Dispatch an event to advance to the next unit operation
			dispatchEvent(new ButtonEvent("NEXT"));
		}

		/***
		 * Member variables
		 **/
		
		// Datagrid header XML
		protected static const SEQUENCERHEADER:XML = 
			<columns widths="16,90%,5%,5,5%,16" gapH="0">
				<frame />
				<rows heights="15%,85%" gapV="0">
					<frame />
					<label useEmbedded="true">
						<font face="GothamMedium" color={Styling.TEXT_GRAY1} size="20">
							SEQUENCER
						</font>
					</label>
				</rows>
				<rows heights="8,100%,4" gapV="0">
					<frame />
					<horizontal>
						<button id="previous" alignH="fill" alignV="fill" enabled="true" useEmbedded="true"
								enabledTextColor={Styling.TEXT_GRAY1} disabledTextColor={Styling.TEXT_GRAY6}
								backgroundskinup={getQualifiedClassName(sequencer_arrowBtn_up)}
								backgroundskindown={getQualifiedClassName(sequencer_arrowBtn_down)}
								backgroundskindisabled={getQualifiedClassName(sequencer_arrowBtn_disabled)}
								foregroundskinup={getQualifiedClassName(sequencer_arrowLeft)}
								foregroundskindown={getQualifiedClassName(sequencer_arrowLeft_down)}
								foregroundskindisabled={getQualifiedClassName(sequencer_arrowLeft_disabled)} />
					</horizontal>
				</rows>
				<frame />
				<rows heights="8,100%,4" gapV="0">
					<frame />
					<horizontal>
						<button id="next" alignH="fill" alignV="fill" enabled="true" useEmbedded="true"
								enabledTextColor={Styling.TEXT_GRAY1} disabledTextColor={Styling.TEXT_GRAY6}
								backgroundskinup={getQualifiedClassName(sequencer_arrowBtn_up)}
								backgroundskindown={getQualifiedClassName(sequencer_arrowBtn_down)}
								backgroundskindisabled={getQualifiedClassName(sequencer_arrowBtn_disabled)}
								foregroundskinup={getQualifiedClassName(sequencer_arrowRight)}
								foregroundskindown={getQualifiedClassName(sequencer_arrowRight_down)}
								foregroundskindisabled={getQualifiedClassName(sequencer_arrowRight_disabled)} />
					</horizontal>
				</rows>
			</columns>;
		
		// View components
		protected var m_pPreviousButton:Button;
		protected var m_pNextButton:Button;

		// State references
		protected var m_pSequence:Sequence;
		protected var m_nSelectedComponentID:int = -1;
	}
}
