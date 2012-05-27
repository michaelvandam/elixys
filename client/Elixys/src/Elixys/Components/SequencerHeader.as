package Elixys.Components
{
	import Elixys.Assets.*;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentCassette;
	import Elixys.JSON.State.Column;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.SequenceComponent;
	import Elixys.JSON.State.StateSequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
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
			// Get our mode
			if (xml.@mode.length() > 0)
			{
				m_sMode = xml.@mode[0];
			}
			
			// Call the base constructor
			super(screen, SEQUENCERHEADER, attributes);

			// Get references to view components
			m_pTrash = Form(findViewById("trash"));
			m_pPreviousButton = Button(findViewById("previous"));
			m_pNextButton = Button(findViewById("next"));

			// Set the buttons according to our mode
			switch (m_sMode)
			{
				case Constants.EDIT:
					// Add the trash skin
					m_pTrash.addChild(Utils.AddSkin(sequencer_trashIcon_up, true, this, 
						m_pTrash.attributes.width, m_pTrash.attributes.height));
					
					// Intentional fall-through
					
				case Constants.VIEW:
					// Add event listeners
					m_pPreviousButton.addEventListener(ButtonEvent.CLICK, OnPreviousButton);
					m_pNextButton.addEventListener(ButtonEvent.CLICK, OnNextButton);
					break;
				
				case Constants.RUN:
					// Hide the buttons
					m_pPreviousButton.visible = false;
					m_pNextButton.visible = false;
					break;
			}
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
			var pComponent:SequenceComponent, nIndex:int;
			if ((m_pSequence != null) && (m_nSelectedComponentID != -1))
			{
				// Locate the selected component
				for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
				{
					pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
					if (pComponent.ID == m_nSelectedComponentID)
					{
						break;
					}
				}
				
				// Don't enable anything if we don't have a component or a cassette is selected
				if ((nIndex != m_pSequence.Components.length) && (pComponent.ComponentType != ComponentCassette.COMPONENTTYPE))
				{
					// Locate the first non-cassette component and set the state of the previous button
					for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
					{
						pComponent = m_pSequence.Components[nIndex] as SequenceComponent;
						if (pComponent.ComponentType != ComponentCassette.COMPONENTTYPE)
						{
							// Enable or disable the previous button
							bPreviousEnabled = (pComponent.ID != m_nSelectedComponentID);
							break;
						}
					}
				
					// Check the last unit operation and set the state of the next button
					pComponent = m_pSequence.Components[m_pSequence.Components.length - 1] as SequenceComponent;
					bNextEnabled = (pComponent.ID != m_nSelectedComponentID);
				}
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

		// Hit test the drag target
		public function DragHitTest(pDragTarget:Sprite):Boolean
		{
			// Check if the drag target overlaps the trash can
			var pFullDragRect:Rectangle = pDragTarget.getBounds(stage);
			var pTrashRect:Rectangle = m_pTrash.getBounds(stage);
			if (pTrashRect.intersects(pFullDragRect))
			{
				// Calculate the central 40% of the drag rect and test if the that overlaps the trash can
				var nDragOffsetX:Number = pFullDragRect.width * 0.3;
				var nDragOffsetY:Number = pFullDragRect.height * 0.3;
				var pDragRect:Rectangle = new Rectangle(pFullDragRect.x + nDragOffsetX, pFullDragRect.y + nDragOffsetY,
					pFullDragRect.width - (2 * nDragOffsetX), pFullDragRect.height - (2 * nDragOffsetY));
				return pTrashRect.intersects(pDragRect);
			}
			else
			{
				return false;
			}
		}

		/***
		 * Member variables
		 **/
		
		// Datagrid header XML
		protected static const SEQUENCERHEADER:XML = 
			<columns widths="16,86%,20,45,7%,5,7%,16" gapH="0">
				<frame />
				<rows heights="25%,75%" gapV="0">
					<frame />
					<label useEmbedded="true">
						<font face="GothamBold" color={Styling.TEXT_GRAY1} size="14">
							SEQUENCER
						</font>
					</label>
				</rows>
				<rows heights="7,100%,7" gapV="0">
					<frame />
					<frame id="trash" />
				</rows>
				<frame />
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
								foregroundskindisabled={getQualifiedClassName(sequencer_arrowLeft_disabled)}
								foregroundskinscale="0.8" />
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
								foregroundskindisabled={getQualifiedClassName(sequencer_arrowRight_disabled)}
								foregroundskinscale="0.8" />
					</horizontal>
				</rows>
			</columns>;
		
		// Mode
		protected var m_sMode:String = "";

		// View components
		protected var m_pTrash:Form;
		protected var m_pPreviousButton:Button;
		protected var m_pNextButton:Button;

		// State references
		protected var m_pSequence:Sequence;
		protected var m_nSelectedComponentID:int = -1;
	}
}
