package Elixys.Subviews
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentInstall;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This install subview is an extension of the unit operation subview class
	public class SubviewInstall extends SubviewUnitOperation
	{
		/***
		 * Construction
		 **/
		
		public function SubviewInstall(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			// Call the base constructor
			super(screen, sMode, pElixys, nButtonWidth, ComponentInstall.COMPONENTTYPE, 
				RUN_INSTALL, attributes);
			
			// Get references to the view components
			if (sMode == Constants.RUN)
			{
				m_pRunLabel = UILabel(findViewById("prompt_runlabel"));
			}
		}
		
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
						m_pRunLabel.text = (m_pComponent as ComponentInstall).Message;
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
		
		/***
		 * Member variables
		 **/

		// Run XML
		protected static const RUN_INSTALL:XML = 
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
