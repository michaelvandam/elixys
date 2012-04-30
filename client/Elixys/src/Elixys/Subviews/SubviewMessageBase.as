package Elixys.Subviews
{
	import Elixys.Assets.*;
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This subview message base is an extension of the subview unit operation base class
	public class SubviewMessageBase extends SubviewUnitOperationBase
	{
		/***
		 * Construction
		 **/

		public function SubviewMessageBase(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										 sComponentType:String, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, sMode, pElixys, nButtonWidth, sComponentType, RUN_MESSAGE, attributes);
			
			// Get references to the view components
			if (sMode == Constants.RUN)
			{
				m_pRunLabel = UILabel(findViewById("prompt_runlabel"));
			}
		}

		/***
		 * Member functions
		 **/
		
		// Updates the subview
		protected override function Update():void
		{
			// Make sure we have both a run state and component
			if (m_pRunState && m_pComponent)
			{
				// Update the run label
				if (m_sMode == Constants.RUN)
				{
					if (m_pRunState.WaitingForUserInput)
					{
						m_pRunLabel.text = GetMessage();
					}
					else
					{
						m_pRunLabel.text = "";
					}
				}
			}
			
			// Call the base implementation
			super.Update();
		}
		
		// Adjusts the view component positions
		protected override function AdjustPositions():void
		{
			// Call the base implementation
			super.AdjustPositions();
			
			// Adjust the run label
			if ((m_sMode == Constants.RUN) && m_pRunLabel && (m_pRunLabel.parent is Form))
			{
				var pParent:Form = m_pRunLabel.parent as Form;
				m_pRunLabel.fixwidth = pParent.attributes.width;
				if (m_pRunLabel.textWidth < pParent.attributes.width)
				{
					m_pRunLabel.width = m_pRunLabel.textWidth + 10;
				}
				m_pRunLabel.height = m_pRunLabel.textHeight + 10;
				m_pRunLabel.x = (pParent.attributes.width - m_pRunLabel.width) / 2;
				m_pRunLabel.y = (pParent.attributes.height - m_pRunLabel.height) / 2;
			}
		}
		
		// Returns the message text
		protected function GetMessage():String
		{
			return "";
		}

		/***
		 * Member variables
		 **/
		
		// Run XML
		protected static const RUN_MESSAGE:XML = 
			<columns widths="10%,80%,10%" gapH="0" background={Styling.APPLICATION_BACKGROUND}>
				<frame />
				<frame>
					<label id="prompt_runlabel" useEmbedded="true">
						<font face="GothamMedium" color={Styling.TEXT_BLACK} size="18" />
					</label>
				</frame>
			</columns>;
		
		// View components
		protected var m_pRunLabel:UILabel;
	}
}
