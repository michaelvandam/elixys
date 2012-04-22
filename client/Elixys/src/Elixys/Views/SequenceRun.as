package Elixys.Views
{
	import Elixys.Assets.*;
	import Elixys.Components.Button;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.ComponentCassette;
	import Elixys.JSON.State.RunState;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.SequenceComponent;
	import Elixys.JSON.State.State;
	import Elixys.JSON.State.StateSequence;
	import Elixys.Subviews.SubviewBase;
	import Elixys.Subviews.SubviewUnitOperation;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObjectContainer;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.geom.Point;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.*;
	
	// This sequence run screen is an extension of the base sequence class
	public class SequenceRun extends SequenceBase
	{
		/***
		 * Construction
		 **/
		
		public function SequenceRun(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, SEQUENCERUN, attributes, row, inGroup);

			// Set our mode
			m_sMode = Constants.RUN;
			
			// Get references to the view components
			m_pUnitOperationNumber = UILabel(findViewById("unitoperationnumber"));
			m_pUnitOperationName = UILabel(findViewById("unitoperationname"));
			m_pUnitOperationDescription = UILabel(findViewById("sequencerun_description"));
			m_pUnitOperationTimeDescription = UILabel(findViewById("sequencerun_timedescription"));
			m_pUnitOperationTime = UILabel(findViewById("sequencerun_time"));
			m_pUnitOperationButton = Button(findViewById("sequencerun_button"));
			m_pUnitOperationAlert = UILabel(findViewById("sequencerun_alert"));
			m_pUnitOperationStatus = UILabel(findViewById("sequencerun_status"));
			
			// Add the unit operation number background skin
			 m_pUnitOperationNumberBackground = new sequencer_titleBar_mc() as MovieClip;
			 m_pUnitOperationNumber.parent.addChildAt(m_pUnitOperationNumberBackground, 0);
			 
			 // Add event listeners
			 m_pUnitOperationButton.addEventListener(ButtonEvent.CLICK, OnButtonClick);
			 
			 // Initialize the layout
			 AdjustPositions();
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			// Load the view children first
			if (m_nChildrenLoaded < RUN_LOAD_STEPS)
			{
				// Step 1 is loading the navigation bar
				if (m_nChildrenLoaded == 0)
				{
					LoadNavigationBar("sequencerun_navigationbar_container", NAVIGATION);
				}
				
				// Step 2 is loading the sequencer
				if (m_nChildrenLoaded == 1)
				{
					LoadSequencer("sequencerun_sequencer_container", SEQUENCER);
				}

				// Increment and return
				++m_nChildrenLoaded;
				return true;
			}
			
			// Call the base function to load the base children
			return LoadNextBase(LOAD_STEPS);
		}

		/***
		 * Member functions
		 **/
		
		// Updates the state
		public override function UpdateState(pState:State):void
		{
			// Check if the run state has changed
			var bRunStateChanged:Boolean = true;
			if (m_pStateSequence)
			{
				bRunStateChanged = !RunState.CompareRunStates(pState.ServerState.RunState,
					m_pStateSequence.ServerState.RunState);
			}

			// Call the base implementation
			super.UpdateState(pState);

			// Update the run state
			if (bRunStateChanged)
			{
				UpdateRunState(pState.ServerState.RunState);
			}
		}
		
		// Updates the sequence
		public override function UpdateSequence(pSequence:Sequence):void
		{
			// Call the base implementation and update
			super.UpdateSequence(pSequence);
			UpdateComponentInternal();
		}
		
		// Updates the component
		public override function UpdateComponent(pComponent:ComponentBase):void
		{
			// Call the base implementation and update
			super.UpdateComponent(pComponent);
			UpdateComponentInternal();
		}

		// Updates the component name and type
		protected function UpdateComponentInternal():void
		{
			// Make sure we have both a sequence and component
			if ((m_pSequence == null) || (m_pComponent == null))
			{
				return;
			}
			
			// Update the unit operation number and name
			var nUnitOperationIndex:int = 0, nIndex:int, pSequenceComponent:SequenceComponent;
			for (nIndex = 0; nIndex < m_pSequence.Components.length; ++nIndex)
			{
				// Skip cassettes
				pSequenceComponent = m_pSequence.Components[nIndex] as SequenceComponent;
				if (pSequenceComponent.ComponentType == ComponentCassette.COMPONENTTYPE)
				{
					continue;
				}
					
				// Check for the current component
				if (pSequenceComponent.ID == m_pComponent.ID)
				{
					break;
				}
				else
				{
					++nUnitOperationIndex;
				}
			}
			m_pUnitOperationNumber.text = (nUnitOperationIndex + 1).toString();
			m_pUnitOperationNumber.width = width;
			m_pUnitOperationName.text = m_pComponent.ComponentType;
			
			// Adjust the layout
			AdjustPositions();
		}
		
		// Updates the run state view components
		protected function UpdateRunState(pRunState:RunState):void
		{
			// Set the description
			m_pUnitOperationDescription.text = pRunState.Description;
			
			// Set the time
			if (pRunState.Time != "")
			{
				m_pUnitOperationTimeDescription.text = pRunState.TimeDescription;
				m_pUnitOperationTime.text = pRunState.Time;
				m_pUnitOperationTimeDescription.visible = true;
				m_pUnitOperationTime.visible = true;
			}
			else
			{
				m_pUnitOperationTimeDescription.visible = false;
				m_pUnitOperationTime.visible = false;
			}

			// Show or hide the button
			if (pRunState.UnitOperationButton.Text != "")
			{
				m_pUnitOperationButton.text = pRunState.UnitOperationButton.Text;
				m_pUnitOperationButton.visible = true;
			}
			else
			{
				m_pUnitOperationButton.visible = false;
			}
			
			// Set the user alert
			if (pRunState.UserAlert != "")
			{
				m_pUnitOperationAlert.text = pRunState.UserAlert;
				m_pUnitOperationAlert.parent.visible = true;
			}
			else
			{
				m_pUnitOperationAlert.parent.visible = false;
			}

			// Set the status
			if (pRunState.Status != "")
			{
				m_pUnitOperationStatus.text = "STATUS:\n" + pRunState.Status;
				m_pUnitOperationStatus.visible = true;
			}
			else
			{
				m_pUnitOperationStatus.visible = false;
			}
			
			// Update the subviews
			for (var nIndex:int = 0; nIndex < m_pSubviews.length; ++nIndex)
			{
				(m_pSubviews[nIndex] as SubviewBase).UpdateRunState(pRunState);
			}
			
			// Adjust the layout
			AdjustPositions();
		}

		// Adjusts the view component positions
		protected function AdjustPositions():void
		{
			// Adjust the unit operation number and background skin
			m_pUnitOperationNumber.width = m_pUnitOperationNumber.textWidth + 8;
			var pParent:Form = m_pUnitOperationNumber.parent as Form;
			m_pUnitOperationNumber.x = (pParent.attributes.width - m_pUnitOperationNumber.width) / 2;
			m_pUnitOperationNumber.y = (pParent.attributes.height - m_pUnitOperationNumber.height) / 2;
			m_pUnitOperationNumberBackground.width = m_pUnitOperationNumber.width + 
				(2 * SubviewUnitOperation.UNITOPERATIONHEADERPADDING);
			m_pUnitOperationNumberBackground.height = m_pUnitOperationNumber.height + 
				(2 * SubviewUnitOperation.UNITOPERATIONHEADERPADDING);
			m_pUnitOperationNumberBackground.x = m_pUnitOperationNumber.x - SubviewUnitOperation.UNITOPERATIONHEADERPADDING;
			m_pUnitOperationNumberBackground.y = m_pUnitOperationNumber.y - SubviewUnitOperation.UNITOPERATIONHEADERPADDING;
			
			// Adjust the unit operation name
			m_pUnitOperationName.x = 0;
			m_pUnitOperationName.y = ((m_pUnitOperationName.parent as Form).attributes.height - 
				m_pUnitOperationName.height) / 2;
			
			// Adjust the user alert
			if (m_pUnitOperationAlert.visible)
			{
				pParent = m_pUnitOperationAlert.parent as Form;
				m_pUnitOperationAlert.width = pParent.attributes.width * 0.9;
				m_pUnitOperationAlert.x = (pParent.attributes.width - m_pUnitOperationAlert.width) / 2;
				m_pUnitOperationAlert.y = (pParent.attributes.height - m_pUnitOperationAlert.height) / 2;
			}
		}
		
		// Overridden to handle unit operation button clicks
		protected override function OnButtonClick(event:ButtonEvent):void
		{
			// Intercept and set the target if it was out unit operation button
			if (event.target == m_pUnitOperationButton)
			{
				super.OnButtonClick(new ButtonEvent(m_pStateSequence.ServerState.RunState.UnitOperationButton.ID));
			}
			else
			{
				// Call the base implementation
				super.OnButtonClick(event);
			}
		}

		
		/***
		 * Member variables
		 **/

		// Sequence run XML
		protected static const SEQUENCERUN:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows gapV="0" border="false" heights="18%,61%,21%" alignH="fill" alignV="fill">
					<frame id="sequencerun_navigationbar_container" alignV="fill" alignH="fill" />
					<rows heights="8%,3%,89%" gapV="0" alignV="fill" alignH="fill">
						<frame id="sequence_title_container" />
						<frame />
						<columns widths="20,32%,20,4,64%" gapH="0" alignV="fill" alignH="fill">
							<frame />
							<rows heights="12%,22%,8%,15%,11%,8,11%,5%,16%" gapV="0" alignV="fill" alignH="fill">
								<columns gapH="0" widths="14%,86%">
									<frame>
										<label id="unitoperationnumber" useEmbedded="true">
											<font face="GothamMedium" color={Styling.TEXT_WHITE} size="14" />
										</label>
									</frame>
									<frame>
										<label id="unitoperationname" useEmbedded="true">
											<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
										</label>
									</frame>
								</columns>
								<frame>
									<label id="sequencerun_description" useEmbedded="true">
										<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14" />
									</label>
								</frame>
								<frame alignV="bottom">
									<label id="sequencerun_timedescription" useEmbedded="true">
										<font face="GothamMedium" color={Styling.TEXT_BLACK} size="14" />
									</label>
								</frame>
								<frame>
									<label id="sequencerun_time" useEmbedded="true">
										<font face="GothamBold" color={Styling.TEXT_BLACK} size="32" />
									</label>
								</frame>
								<frame>
									<button id="sequencerun_button" alignH="fill" alignV="fill"
											useEmbedded="true" enabledTextColor={Styling.TEXT_GRAY1} 
											disabledTextColor={Styling.TEXT_GRAY1} pressedTextColor={Styling.TEXT_WHITE}
											backgroundskinup={getQualifiedClassName(sequencer_timerBtn_up)}
											backgroundskindown={getQualifiedClassName(sequencer_timerBtn_down)}
											backgroundskindisabled={getQualifiedClassName(sequencer_timerBtn_up)}>
										<font face="GothamMedium" size="14" />
									</button>
								</frame>
								<frame />
								<frame background={Styling.TEXT_BLUE1}>
									<label id="sequencerun_alert" useEmbedded="true">
										<font face="GothamMedium" color={Styling.TEXT_WHITE} size="14" />
									</label>
								</frame>
								<frame />
								<frame>
									<label id="sequencerun_status" useEmbedded="true">
										<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
									</label>
								</frame>
							</rows>
							<frame />
							<rows heights="9%,85%,6%" gapV="0" alignV="fill" alignH="fill">
								<frame />
								<frame background={Styling.TABBAR_LINE} />
							</rows>
							<frame id="unitoperation_container" />
						</columns>
					</rows>
					<frame id="sequencerun_sequencer_container" alignV="fill" alignH="fill" />
				</rows>
			</frame>;
		
		// Navigation bar XML
		protected static const NAVIGATION:XML =
			<navigationbar alignH="fill" alignV="fill" skin={getQualifiedClassName(blueNavigationBar_mc)} rightpadding="20">
				<navigationbaroption name="SEQUENCER" backgroundskinheightpercent="72" foregroundskinheightpercent="30"
						fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_GRAY1} disabledTextColor={Styling.TEXT_GRAY1}
						backgroundskinup={getQualifiedClassName(mainNav_activeBtnOutline_down)}
						backgroundskindown={getQualifiedClassName(mainNav_activeBtnOutline_down)}
						backgroundskindisabled={getQualifiedClassName(mainNav_activeBtnOutline_down)}
						foregroundskinup={getQualifiedClassName(mainNav_sequencer_active)}
						foregroundskindown={getQualifiedClassName(mainNav_sequencer_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_sequencer_disabled)}>
					SEQUENCER
				</navigationbaroption>
				<navigationbaroption name="PAUSERUN" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(sequencerNav_pauseRun_up)}
						foregroundskindown={getQualifiedClassName(sequencerNav_pauseRun_down)} 
						foregroundskindisabled={getQualifiedClassName(sequencerNav_pauseRun_disabled)}>
					PAUSE RUN
				</navigationbaroption>
				<navigationbaroption name="ABORTRUN" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(sequencerNav_abortRun_up)}
						foregroundskindown={getQualifiedClassName(sequencerNav_abortRun_down)} 
						foregroundskindisabled={getQualifiedClassName(sequencerNav_abortRun_disabled)}>
					ABORT RUN
				</navigationbaroption>
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
			</navigationbar>;
		
		// Sequencer XML
		protected static const SEQUENCER:XML =
			<sequencer mode={Constants.RUN} alignH="fill" alignV="fill"/>;
		
		// Number of steps required to load this object
		public static var RUN_LOAD_STEPS:uint = 2;
		public static var LOAD_STEPS:uint = SequenceBase.BASE_LOAD_STEPS + RUN_LOAD_STEPS;
		
		// View components
		protected var m_pUnitOperationNumber:UILabel;
		protected var m_pUnitOperationNumberBackground:MovieClip;
		protected var m_pUnitOperationName:UILabel;
		protected var m_pUnitOperationDescription:UILabel;
		protected var m_pUnitOperationTimeDescription:UILabel;
		protected var m_pUnitOperationTime:UILabel;
		protected var m_pUnitOperationButton:Button;
		protected var m_pUnitOperationAlert:UILabel;
		protected var m_pUnitOperationStatus:UILabel;
	}
}
